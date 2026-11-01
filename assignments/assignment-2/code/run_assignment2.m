function run_assignment2
% CS5486 Assignment 2: two-input epsilon-SVR and LS-SVM.
% Run from MATLAB: addpath('code'); run_assignment2
% All experimental outputs are regenerated from this single run.
root = fileparts(fileparts(mfilename('fullpath')));
datadir = fullfile(root,'data'); if ~isfolder(datadir), mkdir(datadir); end
solutiondir = fullfile(root,'solution'); if ~isfolder(solutiondir), mkdir(solutiondir); end
dep = fullfile(root,'dependencies','LSSVMlabv1_8_R2009b_R2011a');
assert(isfolder(dep),'Keep the supplied official LS-SVMlab dependency folder.');
oldPath = path; pathCleanup = onCleanup(@() path(oldPath)); %#ok<NASGU>
addpath(dep);
assert(exist('fitrsvm','file')==2,'Statistics and Machine Learning Toolbox is required.');
assert(license('test','Statistics_Toolbox')==1,'Statistics toolbox license unavailable.');
assert(startsWith(which('trainlssvm'),dep),'Unexpected LS-SVMlab on the path.');
figdir = fullfile(root,'figures'); if ~isfolder(figdir), mkdir(figdir); end

rng(5486,'twister');
X = -5+10*rand(100,2);
z = sin(X(:,1)+X(:,2));
dataRngState = rng;
assert(isequal(size(X),[100 2]) && all(X(:)>=-5 & X(:)<=5));
assert(isequal(z,sin(sum(X,2))));
sigma = 1; kernelScale = sqrt(2); sig2 = 1;
% The ACTUAL LS-SVMlab train/sim path calls kernel_matrix, which uses
% exp(-D2/(2*sig2)). The unused standalone RBF_kernel has a different rule.
checks.unitExpected = exp(-0.5);
checks.unitSVR = exp(-sum(([0 0]-[1 0]).^2)/kernelScale^2);
checks.unitLSSVM = kernel_matrix([0 0],'RBF_kernel',sig2,[1 0]);
assert(max(abs([checks.unitSVR checks.unitLSSVM]-checks.unitExpected))<1e-14);
K = gaussianKernel(X,X,sigma);
checks.kernelMatrixDifference = max(abs(K-kernel_matrix(X,'RBF_kernel',sig2)),[],'all');
assert(checks.kernelMatrixDifference<1e-12);

% A single balanced random five-fold partition, made before fitting models.
foldId = zeros(100,1); permutation = randperm(100);
foldId(permutation) = repmat((1:5)',20,1);
assert(all(accumarray(foldId,1)==20));
C0 = [1 10 100 1000]; E0 = [0.001 0.01 0.05 0.1];
G0 = [1 10 100 1000 10000];
cvSVR = tuneSVR(X,z,foldId,C0,E0,table());
cvLS = tuneLS(X,z,foldId,G0,table());
[~,j] = min(cvSVR.MSE); initialSVR = cvSVR(j,:);
[~,j] = min(cvLS.MSE); initialLS = cvLS(j,:);
% Predeclared bounded extension: one extra decade on a winning boundary.
% The decision depends only on CV; the final evaluation grid does not exist yet.
Cgrid = extendBoundary(C0,initialSVR.C);
Egrid = extendBoundary(E0,initialSVR.Epsilon);
Ggrid = extendBoundary(G0,initialLS.Gamma);
cvSVR = tuneSVR(X,z,foldId,Cgrid,Egrid,cvSVR);
cvLS = tuneLS(X,z,foldId,Ggrid,cvLS);
cvSVR = sortrows(cvSVR,{'C','Epsilon'}); cvLS = sortrows(cvLS,'Gamma');
[~,j] = min(cvSVR.MSE); bestSVR = cvSVR(j,:);
[~,j] = min(cvLS.MSE); bestLS = cvLS(j,:);
fprintf('Selected C=%g, epsilon=%g, gamma=%g\n',bestSVR.C,bestSVR.Epsilon,bestLS.Gamma);
svr = fitSVR(X,z,bestSVR.C,bestSVR.Epsilon);
ls = fitLS(X,z,bestLS.Gamma);
checks.svrConvergence = svr.ConvergenceInfo;
assert(svr.ConvergenceInfo.Converged,'Final SVR did not converge.');
assert(isempty(svr.Mu) && isempty(svr.Sigma),'SVR was standardized.');
assert(strcmp(ls.preprocess,'original') && isequal(ls.xtrain,X) && isequal(ls.ytrain,z));
trainSVR = predict(svr,X); trainLS = simlssvm(ls,X);

% Grid is used only after parameter selection and final fitting.
axisValues = linspace(-5,5,101);
[xq,yq] = meshgrid(axisValues,axisValues);
Q = [xq(:) yq(:)]; truth = sin(Q(:,1)+Q(:,2));
predSVR = predict(svr,Q); predLS = simlssvm(ls,Q);
surfaceSVR = reshape(predSVR,size(xq)); surfaceLS = reshape(predLS,size(xq));
probe = sub2ind(size(xq),[2 17 79],[83 4 44]);
assert(isequal(Q(probe,:),[xq(probe)' yq(probe)']));
assert(max(abs(surfaceSVR(probe)'-predict(svr,Q(probe,:))))<1e-12);
assert(max(abs(surfaceLS(probe)'-simlssvm(ls,Q(probe,:))))<1e-12);
checks.gridOrderPassed = true;

% Independent direct-distance Gaussian kernel verifies the built-in SVR
% prediction, including scale, alpha signs, and bias (not merely its docs).
manualSVR = gaussianKernel(Q,svr.SupportVectors,sigma)*svr.Alpha+svr.Bias;
checks.svrManualPredictionDifference = max(abs(predSVR-manualSVR));
assert(checks.svrManualPredictionDifference<1e-10);
A = [0 ones(1,100); ones(100,1) K+eye(100)/bestLS.Gamma];
rhs = [0;z]; theta = A\rhs;
checks.kktRelativeResidual = norm(A*[ls.b;ls.alpha]-rhs)/norm(rhs);
checks.alphaSum = sum(ls.alpha);
checks.alphaIdentityInfinity = norm(ls.alpha-bestLS.Gamma*(z-trainLS),inf);
checks.alphaIdentityRelative = norm(ls.alpha-bestLS.Gamma*(z-trainLS))/max(1,norm(ls.alpha));
manualLS = gaussianKernel(Q,X,sigma)*theta(2:end)+theta(1);
checks.lsKktPredictionDifference = max(abs(predLS-manualLS));
assert(checks.kktRelativeResidual<1e-10 && abs(checks.alphaSum)<1e-8);
assert(checks.alphaIdentityRelative<1e-7 && checks.lsKktPredictionDifference<1e-9);
checks.svrSupportVectors = sum(svr.IsSupportVector);
checks.lsNonzeroCoefficients = sum(abs(ls.alpha)>1e-10);
checks.lsCoefficientMinAbs = min(abs(ls.alpha));
checks.lsCoefficientMaxAbs = max(abs(ls.alpha));

% Warm up BOTH complete training and prediction paths. Fresh LS structs
% avoid trainlssvm's already-trained early return. Explicit tic handles
% are essential because trainlssvm itself invokes a bare tic internally.
for r=1:5
    warmSVR = fitSVR(X,z,bestSVR.C,bestSVR.Epsilon);
    warmLS = fitLS(X,z,bestLS.Gamma);
    predict(warmSVR,Q); simlssvm(warmLS,Q);
end
nRepeat = 40; rawTrainSeconds = zeros(nRepeat,2); rawPredictSeconds = zeros(nRepeat,2);
measuredOrder = zeros(nRepeat,2); timedConverged = false(nRepeat,1);
for r=1:nRepeat
    if mod(r,2)==1, order=[1 2]; else, order=[2 1]; end
    measuredOrder(r,:) = order;
    for modelIndex=order
        if modelIndex==1
            token=tic; timedSVR=fitSVR(X,z,bestSVR.C,bestSVR.Epsilon);
            rawTrainSeconds(r,1)=toc(token);
            timedConverged(r)=timedSVR.ConvergenceInfo.Converged;
        else
            token=tic; timedLS=fitLS(X,z,bestLS.Gamma);
            rawTrainSeconds(r,2)=toc(token);
        end
    end
    for modelIndex=order
        if modelIndex==1
            token=tic; yp=predict(timedSVR,Q); rawPredictSeconds(r,1)=toc(token);
        else
            token=tic; yp=simlssvm(timedLS,Q); rawPredictSeconds(r,2)=toc(token);
        end
        assert(all(isfinite(yp)));
    end
end
assert(all(timedConverged),'A timed SVR fit did not converge.');
checks.allCVConverged = all(cvSVR.AllConverged);
assert(checks.allCVConverged);
metrics = [errors(z,trainSVR) errors(truth,predSVR); errors(z,trainLS) errors(truth,predLS)];
Model = ["epsilon-SVR";"LS-SVM"];
comparison = table(Model,metrics(:,1),metrics(:,2),metrics(:,4),metrics(:,5),metrics(:,6), ...
    1000*median(rawTrainSeconds,1)',1000*iqr(rawTrainSeconds,1)', ...
    1000*median(rawPredictSeconds,1)',1000*iqr(rawPredictSeconds,1)', ...
    [checks.svrSupportVectors;checks.lsNonzeroCoefficients], ...
    'VariableNames',{'Model','TrainRMSE','TrainMAE','GridRMSE','GridMAE','GridMaxAE', ...
    'TrainMedian_ms','TrainIQR_ms','PredictMedian_ms','PredictIQR_ms','ActiveCoefficients'});

metadata.matlabVersion = version;
metadata.release = version('-release'); metadata.products = ver;
statsVersion = ver('stats'); metadata.statisticsVersion=statsVersion.Version;
metadata.architecture = computer; metadata.runTime = char(datetime('now','TimeZone','Asia/Hong_Kong'));
[~,metadata.cpu] = system('sysctl -n machdep.cpu.brand_string'); metadata.cpu=strtrim(metadata.cpu);
[~,ram] = system('sysctl -n hw.memsize'); metadata.ramGiB = str2double(ram)/2^30;
[~,cores] = system('sysctl -n hw.physicalcpu'); metadata.physicalCores=str2double(cores);
[~,metadata.os] = system('sw_vers -productVersion'); metadata.os=strtrim(metadata.os);
metadata.svrSolver=svr.Solver;
metadata.lsSolver='LS-SVMlab 1.8 trainlssvm/lssvmMATLAB; two MATLAB backslash solves';
metadata.lsSource='dependencies/LSSVMlabv1_8_R2009b_R2011a/lssvmMATLAB.m'; metadata.kernelSource='dependencies/LSSVMlabv1_8_R2009b_R2011a/kernel_matrix.m';
metadata.svrSource='MATLAB/Statistics and Machine Learning Toolbox/fitrsvm.m'; metadata.blas=version('-blas');
metadata.warmups=5; metadata.repetitions=nRepeat;
metadata.svrTolerances=struct('GapTolerance',1e-6,'KKTTolerance',1e-6,'IterationLimit',1e6);

writetable(table(X(:,1),X(:,2),z,foldId,'VariableNames',{'x','y','z','CVFold'}),fullfile(datadir,'training_samples.csv'));
writetable(comparison,fullfile(datadir,'comparison.csv'));
plotSamples(X,z,figdir);
plotSurface(xq,yq,surfaceSVR,X,z,trainSVR,'epsilon-SVR',fullfile(figdir,'svr_surface.png'));
plotSurface(xq,yq,surfaceLS,X,z,trainLS,'LS-SVM',fullfile(figdir,'lssvm_surface.png'));
save(fullfile(datadir,'results.mat'),'X','z','foldId','dataRngState','sigma','kernelScale','sig2', ...
    'C0','E0','G0','Cgrid','Egrid','Ggrid','cvSVR','cvLS','initialSVR','initialLS','bestSVR','bestLS', ...
    'svr','ls','trainSVR','trainLS','axisValues','xq','yq','Q','truth','predSVR','predLS', ...
    'surfaceSVR','surfaceLS','checks','comparison','rawTrainSeconds','rawPredictSeconds', ...
    'measuredOrder','timedConverged','metadata');
writeReport(solutiondir,comparison,bestSVR,bestLS,initialSVR,initialLS,cvSVR,cvLS,checks,metadata,Cgrid,Egrid,Ggrid);
disp(comparison); disp(checks); fprintf('Saved assignment outputs in %s\n',root);
end

function mdl=fitSVR(X,z,C,epsilon)
mdl=fitrsvm(X,z,'KernelFunction','gaussian','KernelScale',sqrt(2), ...
    'Standardize',false,'BoxConstraint',C,'Epsilon',epsilon,'Solver','SMO', ...
    'GapTolerance',1e-6,'KKTTolerance',1e-6,'IterationLimit',1e6);
end

function mdl=fitLS(X,z,gamma)
mdl=initlssvm(X,z,'f',gamma,1,'RBF_kernel','original');
mdl=trainlssvm(mdl);
end

function T=tuneSVR(X,z,fold,Cvalues,Evalues,T)
for C=Cvalues
    for e=Evalues
        if ~isempty(T) && any(T.C==C & T.Epsilon==e), continue; end
        foldMSE=zeros(1,5); converged=true;
        for f=1:5
            test=fold==f; mdl=fitSVR(X(~test,:),z(~test),C,e);
            converged=converged && mdl.ConvergenceInfo.Converged;
            foldMSE(f)=mean((predict(mdl,X(test,:))-z(test)).^2);
        end
        assert(converged,'Nonconverged CV fit: C=%g epsilon=%g',C,e);
        row=table(C,e,mean(foldMSE),foldMSE,converged,'VariableNames',{'C','Epsilon','MSE','FoldMSE','AllConverged'});
        T=[T;row]; %#ok<AGROW>
    end
end
end

function T=tuneLS(X,z,fold,Gvalues,T)
for g=Gvalues
    if ~isempty(T) && any(T.Gamma==g), continue; end
    foldMSE=zeros(1,5);
    for f=1:5
        test=fold==f; mdl=fitLS(X(~test,:),z(~test),g);
        foldMSE(f)=mean((simlssvm(mdl,X(test,:))-z(test)).^2);
    end
    row=table(g,mean(foldMSE),foldMSE,'VariableNames',{'Gamma','MSE','FoldMSE'});
    T=[T;row]; %#ok<AGROW>
end
end

function grid=extendBoundary(grid,best)
if best==min(grid), grid=[min(grid)/10 grid];
elseif best==max(grid), grid=[grid 10*max(grid)]; end
end

function K=gaussianKernel(U,V,sigma)
% Direct coordinate differences provide an independent kernel check.
D2=(U(:,1)-V(:,1)').^2+(U(:,2)-V(:,2)').^2;
K=exp(-D2/(2*sigma^2));
end

function e=errors(y,p)
d=p-y; e=[sqrt(mean(d.^2)) mean(abs(d)) max(abs(d))];
end

function styleAxes(ax)
axis(ax,[-5 5 -5 5 -1.3 1.3]); clim(ax,[-1 1]); view(ax,[-38 27]);
xlabel(ax,'x'); ylabel(ax,'y'); zlabel(ax,'z');
set(ax,'FontName','Arial','FontSize',12); grid(ax,'on'); box(ax,'on');
colormap(ax,parula(256));
end

function plotSamples(X,z,folder)
f=figure('Visible','off','Color','w','Position',[100 100 1000 700]);
ax=axes(f); scatter3(ax,X(:,1),X(:,2),z,42,z,'filled','MarkerEdgeColor',[.12 .12 .12]);
styleAxes(ax); title(ax,'100 training samples: z = sin(x + y)');
c=colorbar(ax); c.Label.String='z';
exportgraphics(f,fullfile(folder,'training_samples.png'),'Resolution',200); close(f);
end

function plotSurface(xq,yq,Z,X,z,p,name,outfile)
f=figure('Visible','off','Color','w','Position',[100 100 1000 700]);
ax=axes(f); h1=surf(ax,xq,yq,Z,'EdgeColor','none','FaceAlpha',.86); hold(ax,'on');
h2=scatter3(ax,X(:,1),X(:,2),z,40,'k','o','filled');
h3=scatter3(ax,X(:,1),X(:,2),p,55,[.85 .12 .08],'+','LineWidth',1.4);
styleAxes(ax); title(ax,[name ': predicted surface']);
c=colorbar(ax); c.Label.String='Predicted z';
legend(ax,[h1 h2 h3],{'Grid prediction','True training samples','Predictions at training inputs'}, ...
    'Location','southoutside','Orientation','horizontal','FontSize',10);
exportgraphics(f,outfile,'Resolution',200); close(f);
end

function writeReport(root,T,bs,bl,is,il,cvS,cvL,c,m,Cgrid,Egrid,Ggrid)
fid=fopen(fullfile(root,'assignment-2-report.md'),'w','n','UTF-8'); assert(fid>=0);
closer=onCleanup(@() fclose(fid)); %#ok<NASGU>
fprintf(fid,'%s\n', '---', 'header-includes:', '  - \usepackage{float}', '  - \floatplacement{figure}{H}', '---', '');
fprintf(fid,'# CS5486 Assignment 2\n\n');
fprintf(fid,'## Experiment and models\n\n');
fprintf(fid,'Using `rng(5486,''twister'')`, I generated `X=-5+10*rand(100,2)` and `z=sin(X(:,1)+X(:,2))`. Both models used the same 100 noiseless samples. The two input coordinates were kept unchanged, with no standardization or reduction to one input.\n\n');
fprintf(fid,'The fixed Gaussian kernel was\n\n');
fprintf(fid,'%s\n\n','$$K(u,v)=\exp\!\left(-\frac{\|u-v\|^2}{2\sigma^2}\right),\qquad \sigma=1.$$');
fprintf(fid,'MATLAB''s [Gaussian kernel](https://www.mathworks.com/help/stats/fitrsvm.html) divides inputs by `KernelScale`, then uses $\\exp(-D^2)$. Thus `KernelScale=sqrt(2)` gives the required kernel. In the downloaded [LS-SVMlab 1.8](https://www.esat.kuleuven.be/stadius/lssvmlab/toolbox.html), both training and prediction call `kernel_matrix.m`, which uses $\\exp[-D^2/(2\\,\\mathrm{sig2})]$, so I used `sig2=1`. The unused standalone `RBF_kernel.m` instead uses $\\exp(-D^2/\\mathrm{sig2})$; its parameter must not be substituted into this call path. These are parameter conversions; $\\sigma$ stays 1. At unit distance, both actual model conventions give %.12f, equal to $e^{-1/2}$.\n\n',c.unitExpected);
fprintf(fid,'For $f(u)=w^T\\phi(u)+b$, epsilon-SVR solves\n\n');
fprintf(fid,'%s\n\n','$$\min_{w,b,\xi,\xi^*}\;\frac12\|w\|^2+C\sum_i(\xi_i+\xi_i^*),$$');
fprintf(fid,'%s\n\n','subject to $z_i-f(X_i)\leq\epsilon+\xi_i$, $f(X_i)-z_i\leq\epsilon+\xi_i^*$, and $\xi_i,\xi_i^*\geq0$. I used `fitrsvm` with the SMO solver.');
fprintf(fid,'LS-SVM minimizes $\\frac12\\|w\\|^2+\\frac{\\gamma}{2}\\sum_i e_i^2$ subject to $z_i=f(X_i)+e_i$. Its 101-by-101 system is\n\n');
fprintf(fid,'%s\n\n','$$\begin{bmatrix}0&\mathbf1^T\\\mathbf1&K+I/\gamma\end{bmatrix}\begin{bmatrix}b\\\alpha\end{bmatrix}=\begin{bmatrix}0\\z\end{bmatrix},\qquad f(u)=\sum_i\alpha_iK(u,X_i)+b.$$');
fprintf(fid,'I used the official `trainlssvm` and `simlssvm`, with `''original''` preprocessing throughout. The installed code calls `lssvmMATLAB`: two MATLAB backslash solves with $H=K+I/\\gamma$, followed by elimination of the bias. No MEX solver was used.\n\n');
fprintf(fid,'## Parameter selection\n\n');
fprintf(fid,'A single random, balanced five-fold split (20 validation samples per fold) was shared by both models. Selection minimized pooled out-of-fold MSE. Initial candidates were $C=\\{1,10,100,1000\\}$, $\\epsilon=\\{0.001,0.01,0.05,0.1\\}$ and $\\gamma=\\{1,10,100,1000,10000\\}$. Kernel width was never tuned.\n\n');
fprintf(fid,'The initial winners were $C=%g$, $\\epsilon=%g$ (MSE %.6f) and $\\gamma=%g$ (MSE %.6f). A predeclared rule added one decade beyond each winning boundary, once. Final candidate sets were `C=%s`, `epsilon=%s`, `gamma=%s`. Any remaining boundary optimum is only the best tested value; the search was not continued indefinitely. All fold scores are saved in `../data/results.mat`.\n\n',is.C,is.Epsilon,is.MSE,il.Gamma,il.MSE,mat2str(Cgrid),mat2str(Egrid),mat2str(Ggrid));
fprintf(fid,'| Model | Selected parameters | Five-fold MSE |\n|:--|:--|--:|\n');
fprintf(fid,'| epsilon-SVR | $C=%g$, $\\epsilon=%g$ | %.6f |\n| LS-SVM | $\\gamma=%g$ | %.6f |\n\n',bs.C,bs.Epsilon,bs.MSE,bl.Gamma,bl.MSE);
fprintf(fid,'Both selected models were refitted on all 100 samples. Only then was a 101-by-101 `meshgrid` from `linspace(-5,5,101)` evaluated. Its 10,201 true targets were used only for final error measurement.\n\n');
fprintf(fid,'\\clearpage\n\n## 3D results\n\n');
fprintf(fid,'![100 true training samples.](../figures/training_samples.png){width=76%%}\n\n');
fprintf(fid,'![epsilon-SVR. Black circles are true samples; red plus signs are predictions at the same training inputs.](../figures/svr_surface.png){width=76%%}\n\n');
fprintf(fid,'\\clearpage\n\n');
fprintf(fid,'![LS-SVM, with the same axes, color limits and viewing angle as epsilon-SVR.](../figures/lssvm_surface.png){width=76%%}\n\n');
fprintf(fid,'## Accuracy and speed\n\n');
fprintf(fid,'RMSE and MAE were calculated separately on the 100 training samples and the full evaluation grid. No percentage error was used because the sine target crosses zero.\n\n');
fprintf(fid,'| Metric | epsilon-SVR | LS-SVM |\n|:--|--:|--:|\n');
labels={'Training RMSE','Training MAE','Grid RMSE','Grid MAE','Grid maximum absolute error'};
vars={'TrainRMSE','TrainMAE','GridRMSE','GridMAE','GridMaxAE'};
for i=1:numel(vars), v=T.(vars{i}); fprintf(fid,'| %s | %.6f | %.6f |\n',labels{i},v(1),v(2)); end
fprintf(fid,'\n| Time (ms) | epsilon-SVR median (IQR) | LS-SVM median (IQR) |\n|:--|--:|--:|\n');
fprintf(fid,'| Retrain on 100 samples | %.4f (%.4f) | %.4f (%.4f) |\n',T.TrainMedian_ms(1),T.TrainIQR_ms(1),T.TrainMedian_ms(2),T.TrainIQR_ms(2));
fprintf(fid,'| Predict 10,201 grid points | %.4f (%.4f) | %.4f (%.4f) |\n\n',T.PredictMedian_ms(1),T.PredictIQR_ms(1),T.PredictMedian_ms(2),T.PredictIQR_ms(2));
[~,better]=min(T.GridRMSE); fprintf(fid,'%s had the lower grid RMSE in this experiment. ',T.Model(better));
fprintf(fid,'Training error alone is insufficient: the grid also contains regions between widely spaced samples, including the domain edges.\n\n');
fprintf(fid,'\\clearpage\n\n');
fprintf(fid,'After five warm-up training and prediction calls per model, I measured 40 fresh fits and 40 grid predictions per model, alternating the order on successive repetitions. Training included initialization, kernel calculation and solving; no Gram matrix was reused. Prediction included its required kernel calculation. Tuning, plots, downloads and file writes were outside the timers. IQR means the 75th percentile minus the 25th percentile. Raw times and measurement order are in `../data/results.mat`.\n\n');
[~,ft]=min(T.TrainMedian_ms); [~,fp]=min(T.PredictMedian_ms);
fprintf(fid,'%s trained %.2f times faster by median time; %s predicted %.2f times faster. SVR retained %d support vectors; LS-SVM had %d coefficients with $|\\alpha_i|>10^{-10}$ (minimum absolute value %.3g, maximum %.3g). LS-SVM avoids iterative constrained optimization by solving a small dense linear system. Prediction cost also depends on the implementation: `simlssvm` evaluates all training centers in blocks, while MATLAB uses its SVR prediction backend. The coefficient counts alone do not determine the measured speed. These results apply to this 100-sample experiment, hardware and solver settings.\n\n',T.Model(ft),max(T.TrainMedian_ms)/min(T.TrainMedian_ms),T.Model(fp),max(T.PredictMedian_ms)/min(T.PredictMedian_ms),c.svrSupportVectors,c.lsNonzeroCoefficients,c.lsCoefficientMinAbs,c.lsCoefficientMaxAbs);
fprintf(fid,'**Environment:** MATLAB %s; Statistics and Machine Learning Toolbox %s; LS-SVMlab 1.8; macOS %s, %s, %.0f GiB RAM.\n', ['R' erase(m.release,'R')],m.statisticsVersion,m.os,m.cpu,m.ramGiB);
end
