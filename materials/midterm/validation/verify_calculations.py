#!/usr/bin/env python3
"""Independently recompute the hand-worked examples; no TeX values are parsed.

Requires Python 3 and NumPy.  Run from any directory.  The forward objectives,
finite differences, direct primal minimizations and least-squares solves here
are deliberately separate from the handwritten derivative calculations.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

import numpy as np


RESULTS = []


def plain(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def compare(name, method, computed, expected, atol=1e-9):
    a, b = np.asarray(computed), np.asarray(expected)
    passed = a.shape == b.shape and bool(np.allclose(a, b, rtol=0, atol=atol))
    RESULTS.append(dict(name=name, method=method, computed=plain(computed),
                        expected=plain(expected), absolute_tolerance=atol,
                        passed=passed))
    return passed


def finite_gradient(function, parameters, step=1e-6):
    p = np.asarray(parameters, dtype=float)
    gradient = np.empty_like(p)
    for j in range(len(p)):
        plus, minus = p.copy(), p.copy()
        plus[j] += step
        minus[j] -= step
        gradient[j] = (function(plus) - function(minus)) / (2 * step)
    return gradient


def sigmoid(value):
    return 1 / (1 + np.exp(-value))


def foundations():
    W = np.array([[1, 2], [-1, 3]], float)
    x, b = np.array([2, -1]), np.array([1, -2])
    u = W @ x + b
    compare('Q04 matrix affine threshold', 'Direct matrix product and H(u>=0)',
            np.r_[W @ x, u, (u >= 0).astype(int), 0.5 * float(u[0] >= 0)**2],
            np.array([0, -5, 1, -7, 1, 0, 0.5]))

    A, d = np.array([[1., 2], [0, 1]]), np.array([1., -1])
    objective = lambda w: 0.5 * np.sum((A @ w - d)**2)
    compare('Q05 quadratic gradient', 'Central differences of scalar square loss',
            finite_gradient(objective, [0, 0]), np.array([-1, -1]), 1e-8)
    minimum = np.linalg.lstsq(A, d, rcond=None)[0]
    compare('Q05 stationary minimum', 'Independent direct least-squares fit',
            np.r_[minimum, objective(minimum)], np.array([3, -1, 0]))
    compare('Q05 Hessian', 'Matrix product A.T @ A', A.T @ A,
            np.array([[1, 2], [2, 5]]))
    compare('Q06 unique system', 'NumPy linear solve',
            np.linalg.solve([[2., 1], [1, -1]], [5., 1]), np.array([2, 1]))
    rank_data = []
    coeff = np.array([[1., 1], [2, 2]])
    for rhs in ([2, 5], [2, 4]):
        rank_data.extend([np.linalg.matrix_rank(coeff),
                          np.linalg.matrix_rank(np.column_stack([coeff, rhs]))])
    compare('Q06 inconsistent and infinite systems', 'Coefficient/augmented ranks',
            np.array(rank_data), np.array([1, 2, 1, 1]))

    bool2 = np.array(list(itertools.product([0, 1], repeat=2)))
    and_gate = (bool2.sum(axis=1) >= 2).astype(int)
    or_gate = (bool2.sum(axis=1) >= 1).astype(int)
    not_gate = np.array([int(not bit) for bit in [0, 1]])
    veto = int(not 1 and 1 + 1 >= 1)
    tlu = int(np.dot([1, 1, -1], [1, 1, 1]) >= 1)
    compare('Q07 M-P veto and gates', 'Exhaustive Boolean truth tables',
            np.r_[veto, tlu, and_gate, or_gate, not_gate],
            np.array([0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0]))
    bool3 = np.array(list(itertools.product([0, 1], repeat=3)))
    decoded = (bool3 @ np.array([1, -1, 1]) >= 2).astype(int)
    compare('Q08 decoder', 'Exhaustive eight rows rather than selected examples',
            decoded, np.array([0, 0, 0, 0, 0, 1, 0, 0]))
    hidden = np.column_stack([bool2[:, 0] & (1-bool2[:, 1]),
                              (1-bool2[:, 0]) & bool2[:, 1]])
    compare('Q09 multilayer XOR', 'Direct Boolean hidden detectors plus OR',
            (hidden.sum(axis=1) >= 1).astype(int), np.array([0, 1, 1, 0]))
    state, sequence = (0, 0), []
    for pulse in [1, 0, 1, 0]:
        oldA, oldB = state
        state = (int((pulse or oldA) and not oldB),
                 int((pulse and oldA) and not oldB))
        sequence.append(state)
    compare('Q10 synchronous recurrent states', 'Frozen-old-state Boolean simulation',
            np.array(sequence), np.array([[1, 0], [1, 0], [1, 1], [0, 0]]))

    design = np.array([[1., 0, 1], [0, 1, 1]])
    target = np.array([1., 2])
    loss = lambda p: 0.5 * np.sum((design @ p-target)**2)
    grad = finite_gradient(loss, np.zeros(3))
    new = -0.1 * grad
    compare('Q12 batch half-square gradient', 'Central differences of full batch objective',
            grad, np.array([-1, -2, -3]), 1e-8)
    compare('Q12 one batch update', 'Independent forward evaluation after update',
            np.r_[new, design @ new, loss(new)],
            np.array([.1, .2, .3, .4, .5, 1.305]), 1e-8)


def neural():
    features = np.c_[list(itertools.product([0, 1], repeat=2)), np.ones(4)]
    target, parameter, updates = np.array([0, 1, 1, 1]), np.zeros(3), 0
    first, epochs = None, 0
    while epochs < 30:
        changed = False
        for xx, yy in zip(features, target):
            prediction = int(parameter @ xx >= 0)
            error = yy-prediction
            if error:
                parameter += error*xx
                updates += 1
                changed = True
        epochs += 1
        if first is None:
            first = parameter.copy()
        if not changed:
            break
    compare('Q13 perceptron OR', 'Independent sequential threshold simulation',
            np.r_[first, parameter, updates, epochs], np.array([0, 1, 0, 1, 1, -1, 5, 4]))
    compare('Q15 capacity counts', 'Integer binomial computation',
            np.array([2*sum(math.comb(3, k) for k in range(3)),
                      2*sum(math.comb(7, k) for k in range(4)), 2**(2**3)]),
            np.array([14, 128, 256]))
    bipolar_new = np.zeros(3) + .5*(-1-1)*np.array([-1, -1, 1])
    compare('Q16 bipolar update', 'Explicit encoded target and threshold output',
            bipolar_new, np.array([1, 1, -1]))

    augx, initial, target = np.array([1., 2, 1]), np.array([.1, -.1, 0]), 1.
    one_loss = lambda p: 0.5*(target-p@augx)**2
    one_grad = finite_gradient(one_loss, initial)
    new = initial-.1*one_grad
    compare('Q17 LMS gradient', 'Finite differences before any update',
            one_grad, np.array([-1.1, -2.2, -1.1]), 1e-8)
    compare('Q17 LMS update and loss', 'Forward scalar residual after finite-difference step',
            np.r_[new, new@augx, one_loss(initial), one_loss(new)],
            np.array([.21, .12, .11, .56, .605, .0968]), 1e-8)
    online = 0.
    for yy in [1., 2.]:
        online -= .1*(online-yy)
    batch = -.1*finite_gradient(lambda p: .5*np.sum((p[0]-np.array([1., 2.]))**2), [0])[0]
    mean = -.1*finite_gradient(lambda p: .25*np.sum((p[0]-np.array([1., 2.]))**2), [0])[0]
    compare('Q18 online batch mean distinction', 'Separate direct objective gradients',
            np.array([online, batch, mean]), np.array([.29, .3, .15]), 1e-8)
    xor_target = np.array([-1., 1, 1, -1])
    compare('Q18 ADALINE XOR least squares', 'Direct least-squares solution of augmented design',
            np.linalg.lstsq(features, xor_target, rcond=None)[0], np.zeros(3))
    compare('Q19 perceptron versus continuous residual',
            'Evaluate hard class error and linear residual separately at u=.2',
            np.array([1-int(.2>=0), 1-.2]), np.array([0, .8]))
    bool2 = features[:, :2]
    hA = np.c_[(bool2[:, 0]-bool2[:, 1]-.5>=0),
                (-bool2[:, 0]+bool2[:, 1]-.5>=0)].astype(int)
    outA = (hA.sum(axis=1)-.5>=0).astype(int)
    hB = (bool2.sum(axis=1)-1.5>=0).astype(int)
    outB = (bool2.sum(axis=1)-2*hB-.5>=0).astype(int)
    compare('Q20 MLP and skip-connection XOR forward',
            'Exhaustive forward threshold evaluation in each distinct architecture',
            np.r_[outA, outB], np.array([0, 1, 1, 0, 0, 1, 1, 0]))

    initial = np.array([0., 0, 2, -1])
    def forward(p):
        hh = sigmoid(p[0]+p[1])
        return float(hh), float(sigmoid(p[2]*hh+p[3]))
    nnloss = lambda p: .5*(1-forward(p)[1])**2
    grad = finite_gradient(nnloss, initial)
    new = initial-grad
    hh, oo = forward(new)
    compare('Q21 BP all-parameter gradient', 'Central differences of a forward-only network loss',
            grad, np.array([-1/16, -1/16, -1/16, -1/8]), 2e-8)
    compare('Q21 BP synchronous update', 'Subtract finite-difference gradient once from old parameters',
            new, np.array([1/16, 1/16, 33/16, -7/8]), 2e-8)
    RESULTS.append(dict(name='Q21 forward after update',
                        method='Forward-only recomputation; loss must decrease',
                        computed=dict(hidden=hh, output=oo, old_loss=nnloss(initial), new_loss=nnloss(new)),
                        expected='0 <= new_loss < old_loss=1/8',
                        passed=bool(0 <= nnloss(new) < nnloss(initial))))

    hidden_bias = math.log(4)+.8
    # The local downstream loss -delta_1*u_1-delta_2*u_2 has the
    # prescribed upstream deltas.  Differencing it tests the hidden branch sum.
    local_loss = lambda p: -.1*(.5*sigmoid(-2*p[0]+hidden_bias)) + .2*(-.3*sigmoid(-2*p[0]+hidden_bias))
    hidden_grad = finite_gradient(local_loss, [.4])[0]
    delta_change = -.05*hidden_grad+.8*.01
    compare('Q22 hidden branches and momentum', 'Finite differences of two downstream branches, then signed momentum',
            np.array([hidden_grad, delta_change, .4+delta_change]),
            np.array([.0352, .00624, .40624]), 1e-8)

    scaled_tanh = lambda pp: float((1-np.exp(-pp[0]))/(1+np.exp(-pp[0])))
    slope_logistic = lambda pp: float(sigmoid(2*pp[0]))
    compare('Q23 scaled activation derivatives',
            'Central differences of full original exponential expressions',
            np.array([finite_gradient(scaled_tanh, [math.log(4)])[0],
                      finite_gradient(slope_logistic, [0])[0]]), np.array([.32, .5]), 1e-8)
    g2 = lambda xx: xx+4*xx*(1-xx)
    compare('Q24 equal training fits different interpolation',
            'Direct function evaluation at training points and unseen midpoint',
            np.array([g2(0), g2(1), g2(.5), .5*(g2(.5)-.5)**2]),
            np.array([0, 1, 1.5, .5]))
    q25_centers = np.array([[0., 0.], [1., 1.]])
    q25_features = np.exp(-np.sum((np.array([[1., 0.], [0., 0.]])[:, None, :]
                                  -q25_centers[None, :, :])**2, axis=2))
    compare('Q25 RBF width conventions',
            'Direct squared-distance Gaussian evaluations for both denominator conventions',
            np.r_[q25_features.ravel(), math.exp(-.25), math.exp(-.5)],
            np.array([math.exp(-1), math.exp(-1), 1, math.exp(-2), .7788007830714049, .6065306597126334]))

    variance = 1/math.log(2)
    centers = np.array([0., 1.])
    Phi = np.exp(-(centers[:, None]-centers[None, :])**2/variance)
    output_weight = np.linalg.lstsq(Phi, [1., 0.], rcond=None)[0]
    prediction = np.exp(-(.5-centers)**2/variance)@output_weight
    compare('Q26 RBF feature solve', 'Gaussian forward design plus independent least squares',
            np.r_[Phi.ravel(), output_weight, prediction],
            np.array([1, .5, .5, 1, 4/3, -2/3, (2/3)*2**(-1/4)]))
    inputs = np.array(list(itertools.product([0., 1.], repeat=2)))
    rbf_centers = np.array([[1., 1.], [0, 0]])
    basis = np.exp(-np.sum((inputs[:, None, :]-rbf_centers[None, :, :])**2, axis=2))
    score = .9-basis.sum(axis=1)
    compare('Q27 Gaussian XOR mapping', 'Direct two-dimensional squared distances',
            score, np.array([.9-1-math.exp(-2), .9-2/math.e, .9-2/math.e, .9-1-math.exp(-2)]))
    elm_input = np.array([0., 1.])
    H = np.c_[sigmoid(math.log(3)*elm_input), sigmoid(-math.log(3)*elm_input)]
    beta = np.linalg.lstsq(H, [0., 1.], rcond=None)[0]
    elm_predict = np.array([sigmoid(-math.log(3)), sigmoid(math.log(3))])@beta
    compare('Q28 ELM fixed features', 'Independent hidden forward matrix and least-squares output fit',
            np.r_[H.ravel(), beta, elm_predict], np.array([.5, .5, .75, .25, 2, -2, -1]))
    fln = inputs[:, 0]+inputs[:, 1]-2*inputs[:, 0]*inputs[:, 1]
    compare('Q28 FLN XOR expansion', 'Exhaustive explicit cross-product features',
            fln, np.array([0, 1, 1, 0]))


def svm_and_kernels():
    w, bb, xx = np.array([3., 4.]), -5., np.array([1., 1.])
    score = w@xx+bb
    compare('Q31 scaled geometric margin', 'Distances computed from both parameter scales',
            np.array([np.linalg.norm(w), score, score/np.linalg.norm(w),
                      (2*w@xx+2*bb)/np.linalg.norm(2*w)]), np.array([5, 2, .4, .4]))
    x, labels = np.array([-1., 1.]), np.array([-1., 1.])
    grid_w = np.linspace(0, 2, 801)
    grid_b = np.linspace(-1, 1, 801)
    scores = grid_w[:, None, None]*x + grid_b[None, :, None]
    feasible = np.all(labels*scores >= 1-1e-12, axis=2)
    values = np.where(feasible, .5*grid_w[:, None]**2, np.inf)
    i, j = np.unravel_index(values.argmin(), values.shape)
    compare('Q32 hard SVM primal', 'Exhaustive direct primal feasibility/objective grid',
            np.array([grid_w[i], grid_b[j], values[i, j]]), np.array([1, 0, .5]))
    duala = np.linspace(0, 1, 10001)
    dualvalue = 2*duala-2*duala**2
    idx = dualvalue.argmax()
    compare('Q33 hard SVM dual', 'Independent one-dimensional dual search',
            np.array([duala[idx], dualvalue[idx]]), np.array([.5, .5]))
    xx = np.array([-2., -1, 1, 1, 2])
    yy = np.array([-1., -1, 1, 1, 1])
    alpha = np.array([0., .5, .5, 0, 0])
    recovered = (alpha*yy)@xx
    compare('Q34 support coefficients and degenerate boundary', 'Direct labelled expansion and KKT products',
            np.r_[recovered, -.25*recovered, yy*(recovered*xx), alpha*(yy*recovered*xx-1)],
            np.r_[1, -.25, [2, 1, 1, 1, 2], np.zeros(5)])
    margins = np.array([1.4, 1, .6, 0, -.4])
    slack = np.maximum(0, 1-margins)
    compare('Q35 soft slack and cost', 'Direct minimal feasible nonnegative slack',
            np.r_[slack, .5*2**2+2*slack.sum()], np.array([0, 0, .4, 1, 1.4, 7.6]))
    a = np.linspace(0, .25, 10001)
    objective = 2*a-2*a*a
    idx = objective.argmax()
    compare('Q36 soft SVM boxed optimum', 'Independent bounded dual grid',
            np.array([a[idx], 2*a[idx], objective[idx]]), np.array([.25, .5, .375]))
    phi = lambda zz: np.array([1, zz[0]**2, math.sqrt(2)*zz[0]*zz[1], zz[1]**2,
                               math.sqrt(2)*zz[0], math.sqrt(2)*zz[1]])
    # Use both the published exercise points and a nonzero cross-term pair.
    mapped_values, kernel_values = [], []
    for aa, bb in [([1., 0], [0., 1]), ([1., 2], [2., -1]), ([2., 3], [-1., 4])]:
        mapped_values.append(phi(aa)@phi(bb))
        kernel_values.append((1+np.dot(aa, bb))**2)
    compare('Q37 polynomial map identity', 'Independent explicit feature dot versus scalar polynomial',
            np.array(mapped_values), np.array(kernel_values))
    K, invalid = np.array([[4., 1], [1, 4]]), np.array([[1., 2], [2, 1]])
    cc = np.array([1., -1])
    compare('Q38 PSD and invalid Gram', 'Symmetric eigensolver and negative quadratic witness',
            np.r_[np.linalg.eigvalsh(K), cc@invalid@cc], np.array([3, 5, -2]))
    rho = math.exp(-2)
    K = np.array([[1., rho], [rho, 1]])
    alpha, yy = np.ones(2), np.array([-1., 1])
    d = alpha*yy
    scores = K@d
    slack = np.maximum(0, 1-yy*scores)
    primal = .5*d@K@d+slack.sum()
    dual = alpha.sum()-.5*d@K@d
    compare('Q39 Gaussian classification prediction', 'Kernel distances, labelled prediction, independent objectives',
            np.r_[scores[1], primal, dual, slack], np.array([1-rho, 1+rho, 1+rho, rho, rho]))
    compare('Q39 alternative width denominator', 'Re-evaluate exponential with denominator sigma squared',
            np.array([math.exp(-4), 1-math.exp(-4)]),
            np.array([.01831563888873418, .9816843611112658]))


def svr():
    residual = np.array([0., .3, 1.2, -.9])
    xi, star = np.maximum(0, residual-.5), np.maximum(0, -residual-.5)
    compare('Q41 SVR two slack sides', 'Direct residual inequalities and epsilon-insensitive loss',
            np.r_[xi, star, (xi+star).sum()], np.array([0, 0, .7, 0, 0, 0, 0, .4, 1.1]))
    for name, x, y, C, eps, alpha, alpha_star, expected_b, expected_cost in [
        ('Q43 free SVR', np.array([0., 2.]), np.array([0., 2.]), 1., .5,
         np.array([0., .25]), np.array([.25, 0]), .5, .125),
        ('Q44 no-free SVR', np.array([0., 1.]), np.array([0., 2.]), .5, .5,
         np.array([0., .5]), np.array([.5, 0]), .75, .375),
    ]:
        d, K = alpha-alpha_star, np.outer(x, x)
        ww = d@x
        residual = y-(ww*x+expected_b)
        xi, star = np.maximum(0, residual-eps), np.maximum(0, -residual-eps)
        products = np.r_[alpha*(eps+xi-residual), alpha_star*(eps+star+residual),
                          (C-alpha)*xi, (C-alpha_star)*star]
        primal = .5*ww**2+C*(xi+star).sum()
        dual = -.5*d@K@d-eps*(alpha+alpha_star).sum()+y@d
        compare(name+' KKT and objectives', 'Separate primal residual/slack cost versus kernel dual and complementarity',
                np.r_[ww, d.sum(), products, primal, dual],
                np.r_[.5, 0, np.zeros(8), expected_cost, expected_cost])
        # Enumerate the original (w,b) objective, not the dual derivation.
        wg, bg = np.linspace(-.5, 1.5, 401), np.linspace(-.5, 2.5, 601)
        rgrid = y[None, None, :]-(wg[:, None, None]*x[None, None, :]+bg[None, :, None])
        grid_cost = .5*wg[:, None]**2+C*np.maximum(0, np.abs(rgrid)-eps).sum(axis=2)
        wi, _ = np.unravel_index(grid_cost.argmin(), grid_cost.shape)
        compare(name+' direct primal minimum', 'Exhaustive 401 by 601 original-objective grid',
                np.array([wg[wi], grid_cost.min()]), np.array([.5, expected_cost]))
        if 'no-free' in name:
            min_b = bg[np.isclose(grid_cost[wi], expected_cost, atol=1e-12, rtol=0)]
            compare('Q44 no-free bias interval', 'All primal-grid minimizers at optimal w',
                    np.array([min_b.min(), min_b.max()]), np.array([.5, 1]))
    alpha, alpha_star, C, eps, residual = .25, .25, 1., 0., 0.
    compare('Q44 epsilon zero both multipliers positive', 'Explicit one-point primal/dual KKT witness',
            np.array([alpha-alpha_star, alpha*(eps-residual), alpha_star*(eps+residual),
                      -eps*(alpha+alpha_star)]), np.zeros(4))


def lssvm():
    x, y = np.array([0., 1.]), np.array([0., 2.])
    for gamma, expected in [(1., np.array([2/3, 2/3, -2/3, 2/3])),
                             (2., np.array([1., .5, -1., 1.]))]:
        # Solve the ORIGINAL objective in primal parameters (w,b), with no
        # kernel block equations used to obtain the solution.
        X = np.c_[x, np.ones(len(x))]
        penalty = np.diag([1., 0.])
        p = np.linalg.solve(penalty+gamma*X.T@X, gamma*X.T@y)
        error = y-X@p
        alpha = gamma*error
        compare(f'LS-SVM gamma={gamma:g} independent primal solution',
                'Regularized primal normal equations in w,b; alpha obtained only afterwards from residual',
                np.r_[p, alpha], expected)
        kernel = np.outer(x, x)
        block = np.block([[kernel+np.eye(len(x))/gamma, np.ones((len(x), 1))],
                          [np.ones((1, len(x))), np.zeros((1, 1))]])
        block_residual = block@np.r_[alpha, p[1]]-np.r_[y, 0.]
        compare(f'LS-SVM gamma={gamma:g} block and stationarity check',
                'Back-substitute primal solution into course block system and finite-difference objective gradient',
                np.r_[block_residual, finite_gradient(lambda v: .5*v[0]**2+gamma*.5*np.sum((y-X@v)**2), p)],
                np.zeros(5), 2e-8)
        RESULTS.append(dict(name=f'LS-SVM gamma={gamma:g} original Hessian',
                            method='Symmetric primal Hessian eigenvalues prove strict convexity',
                            computed=np.linalg.eigvalsh(penalty+gamma*X.T@X).tolist(),
                            expected='all eigenvalues positive',
                            passed=bool(np.all(np.linalg.eigvalsh(penalty+gamma*X.T@X)>0))))

    # A separate nonlinear feature model for the three-point transfer question.
    x, y = np.array([-1., 0., 1.]), np.array([1., 0., 1.])
    mapped = x*x
    design = np.c_[mapped, np.ones(3)]
    p = np.linalg.solve(np.diag([1., 0.])+design.T@design, design.T@y)
    error = y-design@p
    alpha = error.copy()  # gamma=1, obtained after the independent primal solve
    kernel = np.outer(mapped, mapped)
    cost = .5*p[0]**2+.5*error@error
    compare('Q50 nonlinear three-point LS-SVM',
            'Original squared-feature primal objective solved in w,b; forward residual check',
            np.r_[p, alpha, design@p, error, 4*p[0]+p[1], cost],
            np.array([.4, .4, .2, -.4, .2, .8, .4, .8, .2, -.4, .2, 2, .2]))
    block = np.block([[kernel+np.eye(3), np.ones((3, 1))],
                      [np.ones((1, 3)), np.zeros((1, 1))]])
    compare('Q50 nonlinear block back-substitution',
            'Back-substitute independently fitted coefficients into kernel block equations',
            block@np.r_[alpha, p[1]]-np.r_[y, 0.], np.zeros(4))

    # Check the symbolic gamma-transfer formula at values other than the
    # two examples, so a coincidental numerical agreement is insufficient.
    values, expected = [], []
    for gamma in [.25, .5, 3., 7.]:
        design = np.array([[0., 1.], [1., 1.]])
        p = np.linalg.solve(np.diag([1., 0.])+gamma*design.T@design,
                            gamma*design.T@np.array([0., 2.]))
        values.extend(p)
        expected.extend([2*gamma/(gamma+2), 2/(gamma+2)])
    compare('Q48 general gamma-transfer formula',
            'Independent primal normal solves at four unseen positive gamma values',
            np.array(values), np.array(expected))


def mixed_selftest():
    # Q52: three independently initialized interpretations of the same unit.
    old = np.array([.2, .1])
    features = np.array([1., 1.])
    prediction = int(old@features >= 0)
    perceptron_new = old+.1*(1-prediction)*features
    linear_loss = lambda pp: .5*(1-pp@features)**2
    sigmoid_loss = lambda pp: .5*(1-sigmoid(pp@features))**2
    linear_grad = finite_gradient(linear_loss, old)
    sigmoid_grad = finite_gradient(sigmoid_loss, old)
    lms_new, sigmoid_new = old-.1*linear_grad, old-.1*sigmoid_grad
    compare('Q52 three distinct update rules',
            'Hard decision plus separate finite-difference linear and sigmoid forward losses',
            np.r_[perceptron_new, lms_new, sigmoid_new],
            np.array([.2, .1, .27, .17, .21040311, .11040311]), 1e-8)
    compare('Q52 sigmoid rounded gradient',
            'Central difference checks the full forward loss, without differentiating a hand-coded delta',
            np.array([sigmoid(old@features), -sigmoid_grad[0], -sigmoid_grad[1]]),
            np.array([.57444252, .10403106, .10403106]), 1e-8)
    compare('Q52 LMS before and after losses',
            'Direct loss evaluation at the independently computed update',
            np.array([linear_loss(old), linear_loss(lms_new)]), np.array([.245, .1568]), 1e-8)

    # Q53: candidate bias must be checked independently of multiplier signs.
    x, y, alpha = np.array([-2., 2.]), np.array([-1., 1.]), np.array([1/8, 1/8])
    w = (alpha*y)@x
    bad_margin, good_margin = y*(w*x+1), y*w*x
    corrected_b = y-w*x
    primal, dual = .5*w*w, alpha.sum()-.5*((alpha*y)@x)**2
    compare('Q53 wrong bias and corrected hard SVM',
            'Direct primal margins, two independent support-vector biases and objectives',
            np.r_[w, bad_margin, corrected_b, good_margin, 2/abs(w), primal, dual],
            np.array([.5, 0, 2, 0, 0, 1, 1, 4, .125, .125]))
    compare('Q53 scaling invariance',
            'Re-evaluate functional and geometric margins after parameter scaling',
            np.r_[y*(2*w*x), y*(w*x)/abs(w), y*(2*w*x)/abs(2*w)],
            np.array([2, 2, 2, 2, 2, 2]))

    # Q54 is intentionally only a formal algebra calculation with an invalid
    # kernel; solving it must never be reported as validating that kernel.
    K, H = np.array([[1., 2.], [2., 1.]]), np.array([[3., 2.], [2., 3.]])
    witness = np.array([1., -1.])
    block = np.block([[H, np.ones((2, 1))],
                      [np.ones((1, 2)), np.zeros((1, 1))]])
    solution = np.linalg.solve(block, [0., 2., 0.])
    fitted = K@solution[:2]+solution[2]
    residual = np.array([0., 2.])-fitted
    compare('Q54 invalid kernel versus solvable formal system',
            'Negative quadratic witness, eigensolver and direct augmented linear solve',
            np.r_[witness@K@witness, np.linalg.eigvalsh(H), solution, fitted, residual],
            np.array([-2, 1, 5, -1, 1, 1, 2, 0, -2, 2]))
    compare('Q54 formal residual relation',
            'Back-substitute without claiming an original feature-space optimization',
            residual-solution[:2]/.5, np.zeros(2))

    # Q55: the original primal predictor remains optimal, but changing epsilon
    # changes the old dual multipliers' complementary-slackness products.
    alpha = alpha_star = 2/5
    for eps, expected_products, expected_dual in [
            (0., np.array([0., 0.]), 0.),
            (.5, np.array([.2, .2]), -.4)]:
        products = np.array([alpha*eps, alpha_star*eps])
        dual = -eps*(alpha+alpha_star)
        compare(f'Q55 original multipliers epsilon={eps:g}',
                'Direct complementary-slackness and dual-objective evaluation',
                np.r_[products, dual], np.r_[expected_products, expected_dual])
    # In the corrected epsilon=.5 certificate alpha=alpha*=0; the residual,
    # both slacks and w vanish, while eta=eta*=C=1.
    residual, eps, C = 0., .5, 1.
    corrected_alpha, corrected_star, slack, slack_star = 0., 0., 0., 0.
    compare('Q55 corrected positive-width KKT certificate',
            'Explicit primal/dual zero-objective and complementary-slackness witness',
            np.array([corrected_alpha-corrected_star,
                      corrected_alpha*(eps+slack-residual),
                      corrected_star*(eps+slack_star+residual),
                      (C-corrected_alpha)*slack,
                      (C-corrected_star)*slack_star,
                      -eps*(corrected_alpha+corrected_star)]), np.zeros(6))

    # Q56: independent primal fit recovers B; test error is unregularized and
    # is a DIFFERENT objective from the training objective.
    design = np.array([[0., 1.], [1., 1.]])
    target = np.array([0., 2.])
    B = np.linalg.solve(np.diag([1., 0.])+design.T@design, design.T@target)
    A = np.array([2., 0.])
    training_cost = lambda pp: .5*pp[0]**2+.5*np.sum((target-design@pp)**2)
    test_feature = np.array([2., 1.])
    test_prediction = np.array([test_feature@A, test_feature@B])
    test_error = (4-test_prediction)**2
    compare('Q56 regularized training versus held-out squared error',
            'Original primal normal solve followed by separate unregularized test evaluation',
            np.r_[training_cost(A), training_cost(B), test_prediction, test_error],
            np.array([2, 2/3, 4, 2, 0, 4]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path,
                        default=Path(__file__).with_name('calculation-results.json'))
    args = parser.parse_args()
    foundations()
    neural()
    svm_and_kernels()
    svr()
    lssvm()
    mixed_selftest()
    payload = dict(scope='Independent numerical checks for the paired CS5486 revision PDFs',
                   source='Handwritten examples; no answer generation or TeX parsing',
                   total=len(RESULTS), passed=sum(r['passed'] for r in RESULTS),
                   failed=sum(not r['passed'] for r in RESULTS), results=RESULTS)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(dict(total=payload['total'], passed=payload['passed'],
                          failed=payload['failed'], output=str(args.output.resolve())), ensure_ascii=False))
    for result in RESULTS:
        if not result['passed']:
            print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(1 if payload['failed'] else 0)


if __name__ == '__main__':
    main()
