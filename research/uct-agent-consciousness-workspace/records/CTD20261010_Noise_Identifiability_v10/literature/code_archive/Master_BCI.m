%% Master script for EEG/tACSS data
% This script and corresponding subscripts have been written by Dr. Marie
% Chancel and are used in the study "Parietal alpha frequency shapes
% own-body perception by modulating the temporal integration of bodily
% signals" by Dr D'Angelo et al. 

%% Data sorting and experiment details

SourceFolder='~/Script_OSF';
SourceFile='DatatACS1905.xlsx';

% load the data correspondig to the EEG study
ResponseFile=[SourceFolder char ('/') char(SourceFile)]; % 1 raw = 1 participant // the first 9 columns are the ownership judgments, the last 9 are the simultaneity judgment
DataEEG=xlsread(ResponseFile,2,'B3:S48');
EEG_n_subj=length(DataEEG); % number of participants
EEG_n_cond=2; % 2 tasks
EEG_n_trials=15; % 15 rep for each tested stimuli
EEG_n_asynch=9; % number of tested asynchrony
EEG_Asynch=[-400,-300,-200,-100,0,100,200,300,400]; % Asynchronies in ms
EEG_SigmaS=std([-400,-300,-200,-100,100,200,300,400]); % SigmaS corresponds to the true standard deviation of the asynchronies presented to the participants


% load the data correspondig to the tACS study
ResponseFile=[SourceFolder char ('/') char(SourceFile)]; % 1 raw = 1 participant // the first 21 columns are the ownership judgments, the last 21 are the simultaneity judgment
DatatACS=xlsread(ResponseFile,1,'B4:AQ33');
tACS_n_subj=length(DatatACS(:,1));
tACS_n_cond=6; % 2 tasks x 3 tACS condition
tACS_n_trials=10;
tACS_n_asynch=7;
tACS_Asynch=[-400,-200,-100,0,100,200,400];
tACS_SigmaS=std([-400,-200,-100,100,200,400]);

%% Study EEG - Fit procedure
% We want to know which model best describe the data. Each model has a certain amount of free parameters. We call the vector of parameters Theta. 
% Fitting a model consists in finding the best combination of free parameters to describe each participants individually.
% We use an optimization algorithm (bads) that will maximize the log-likelihood of the model (= minimize the negative log-likelihood)

% To avoid local optimization, we try with different initial sets of parameters n_runs
n_runs = 100; 

% Bayesian Causal Inference model (BCI) for ownership and simultaneity task 
% In this model, the decision criterion takes into account the level of sensory uncertainty 
% we fit the log value because it's more efficient.
%Theta= [Psame_O, Psame_S, LSigma, LSigmaS, lapse];
n_pars = 5; 

% We need to define the range for each parameter
    lb =  [0    0    -10  log(EEG_SigmaS)   eps];        % Hard lower bound
    ub =  [1    1     10  log(EEG_SigmaS)   1];          % Hard upper bound
    PLB = [0.3  0.3   0   log(EEG_SigmaS)   0.001];      % Plausible lower bound
    PUB = [0.7  0.7   6   log(EEG_SigmaS)   0.2];        % Plausible upper bound

       
mkdir([SourceFolder char('Output_EEG')])
cd([SourceFolder char('Output_EEG')])
EEG_all_min_pars= NaN(EEG_n_subj, n_pars); 
EEG_all_min_NLL = NaN(EEG_n_subj, 1);

 for subj=1:EEG_n_subj
 % We organize the response for each participant
 %line 1: ownership | line 2: simulateneity 
    counts_yes = DataEEG(subj,:);
    counts_yes = reshape(counts_yes, [EEG_n_asynch, EEG_n_cond])'; 
    counts_no  = EEG_n_trials - counts_yes;
    
    NLLwithdata = @(pars) NLL_BCI_EEG(pars, EEG_Asynch, counts_yes, counts_no);
    
    % Random initial set of params (careful: we fit log(sigma) not sigma)
    X0(:,1:2)   = 0.3 + 0.4 * rand(n_runs,2);
    X0(:,3) = log(200 * rand(n_runs,1)); 
    X0(:,4)   = log(EEG_SigmaS);                    
    X0(:,5)   = 0.2 * rand(n_runs,1);
    
   % We want to select the set of estimated parameters corresponding to the minimum NLL
    EEG_min_pars = NaN(n_runs, n_pars); 
    EEG_min_NLL  = NaN(n_runs,1);
    
   for run = 1:n_runs
   [min_pars, min_NLL] = bads(NLLwithdata, X0(run,:),lb,ub,PLB,PUB);
    EEG_min_NLL(run)    = min_NLL;
    EEG_min_pars(run,:) = min_pars;
    end
    
    [EEG_all_min_NLL(subj), idx] = min(EEG_min_NLL);
    EEG_all_min_pars(subj,:) = EEG_min_pars(idx, :);
   
    % We save each individual run to double check later
    EEG_Ind_run= [EEG_min_pars,EEG_min_NLL];
    IndividualRunMatrix= [char('EEG_') char(num2str(n_runs)) char('runs_S') char(num2str(subj))];
        save(IndividualRunMatrix, 'EEG_Ind_run')
 end
EEG_all=[EEG_all_min_pars,EEG_all_min_NLL];
save('EEG_all', 'EEG_all')


%% Study tACS - Fit procedure

% To avoid local optimization, we try with different initial sets of parameters n_runs
n_runs = 100; 

% 1st version - different Sigma
cd(SourceFolder)
mkdir([SourceFolder char('Output_tACS_Sigma')])
cd([SourceFolder char('Output_tACS_Sigma')])

% Bayesian Causal Inference model (BCI) for ownership and simultaneity task 
% In this model, the decision criterion takes into account the level of sensory uncertainty 
% we fit the log value because it's more efficient.
%Theta= [Psame_O, Psame_S, LSigma_Low, LSigma_Sham, LSigma_High, LSigmaS, lapse];
n_pars = 7; 
tACS_all_min_pars_Sigma= NaN(tACS_n_subj, n_pars); 
tACS_all_min_NLL_Sigma = NaN(tACS_n_subj, 1);

% We need to define the range for each parameter
    lb =  [0    0    -10  -10  -10  log(tACS_SigmaS)   eps];        % Hard lower bound
    ub =  [1    1     10   10   10  log(tACS_SigmaS)   1];          % Hard upper bound
    PLB = [0.3  0.3   0   0   0   log(tACS_SigmaS)   0.001];      % Plausible lower bound
    PUB = [0.7  0.7   6   6   6   log(tACS_SigmaS)   0.2];        % Plausible upper bound      

 for subj=1:tACS_n_subj
 % We organize the response for each participant
 %line 1: ownership | line 2: simulateneity 
    counts_yes = DatatACS(subj,:);
    counts_yes = reshape(counts_yes, [tACS_n_asynch, tACS_n_cond])'; 
    counts_no  = tACS_n_trials - counts_yes;
    
    NLLwithdata = @(pars) NLL_BCI_tACS_Sigma(pars, tACS_Asynch, counts_yes, counts_no);
    
    % Random initial set of params (careful: we fit log(sigma) not sigma)
    X0(:,1:2)   = 0.3 + 0.4 * rand(n_runs,2);
    X0(:,3:5) = log(200 * rand(n_runs,3)); 
    X0(:,6)   = log(tACS_SigmaS);                    
    X0(:,7)   = 0.2 * rand(n_runs,1);
    
   % We want to select the set of estimated parameters corresponding to the minimum NLL
    tACS_min_pars_Sigma = NaN(n_runs, n_pars); 
    tACS_min_NLL_Sigma  = NaN(n_runs,1);
    
   for run = 1:n_runs
   [min_pars, min_NLL] = bads(NLLwithdata, X0(run,:),lb,ub,PLB,PUB);
    tACS_min_NLL_Sigma(run)    = min_NLL;
    tACS_min_pars_Sigma(run,:) = min_pars;
    end
    
    [tACS_all_min_NLL_Sigma(subj), idx] = min(tACS_min_NLL_Sigma);
    tACS_all_min_pars_Sigma(subj,:) = tACS_min_pars_Sigma(idx, :);
   
    % We save each individual run to double check later
    tACS_Ind_run_Sigma= [tACS_min_pars_Sigma,tACS_min_NLL_Sigma];
    IndividualRunMatrix= [char('tACS_Sigma_') char(num2str(n_runs)) char('runs_S') char(num2str(subj))];
        save(IndividualRunMatrix, 'tACS_Ind_run_Sigma')
 end
tACS_all_Sigma=[tACS_all_min_pars_Sigma,tACS_all_min_NLL_Sigma];
save('tACS_all_Sigma', 'tACS_all_Sigma')




% 2nd version - different psame
cd(SourceFolder)
mkdir([SourceFolder char('Output_tACS_Psame')])
cd([SourceFolder char('Output_tACS_Psame')])

% Bayesian Causal Inference model (BCI) for ownership and simultaneity task 
% In this model, the decision criterion takes into account the level of sensory uncertainty 
% we fit the log value because it's more efficient.
%Theta= [Psame_O_Low, Psame_O_Sham, Psame_O_High, Psame_S_Low, Psame_S_Sham, Psame_S_High, LSigma, LSigmaS, lapse];
n_pars = 9; 
tACS_all_min_pars_Psame= NaN(tACS_n_subj, n_pars); 
tACS_all_min_NLL_Psame = NaN(tACS_n_subj, 1);

% We need to define the range for each parameter
    lb =  [0    0   0    0   0    0     -10  log(tACS_SigmaS)   eps];        % Hard lower bound
    ub =  [1    1   1    1   1    1    10  log(tACS_SigmaS)   1];          % Hard upper bound
    PLB = [0.3  0.3  0.3  0.3  0.3  0.3 0   log(tACS_SigmaS)   0.001];      % Plausible lower bound
    PUB = [0.7  0.7  0.7  0.7  0.7  0.7 6   log(tACS_SigmaS)   0.2];        % Plausible upper bound      


 for subj=21:tACS_n_subj
 % We organize the response for each participant
 %line 1: ownership | line 2: simulateneity 
    counts_yes = DatatACS(subj,:);
    counts_yes = reshape(counts_yes, [tACS_n_asynch, tACS_n_cond])'; 
    counts_no  = tACS_n_trials - counts_yes;
    
    NLLwithdata = @(pars) NLL_BCI_tACS_Psame(pars, tACS_Asynch, counts_yes, counts_no);
    
    % Random initial set of params (careful: we fit log(sigma) not sigma)
    X0(:,1:6)   = 0.3 + 0.4 * rand(n_runs,6);
    X0(:,7) = log(200 * rand(n_runs,1)); 
    X0(:,8)   = log(tACS_SigmaS);                    
    X0(:,9)   = 0.2 * rand(n_runs,1);
    
   % We want to select the set of estimated parameters corresponding to the minimum NLL
    tACS_min_pars_Psame = NaN(n_runs, n_pars); 
    tACS_min_NLL_Psame  = NaN(n_runs,1);
    
   for run = 1:n_runs
   [min_pars, min_NLL] = bads(NLLwithdata, X0(run,:),lb,ub,PLB,PUB);
    tACS_min_NLL_Psame(run)    = min_NLL;
    tACS_min_pars_Psame(run,:) = min_pars;
    end
    
    [tACS_all_min_NLL_Psame(subj), idx] = min(tACS_min_NLL_Psame);
    tACS_all_min_pars_Psame(subj,:) = tACS_min_pars_Psame(idx, :);
   
    % We save each individual run to double check later
    tACS_Ind_run_Psame= [tACS_min_pars_Psame,tACS_min_NLL_Psame];
    IndividualRunMatrix= [char('tACS_Psame_') char(num2str(n_runs)) char('runs_S') char(num2str(subj))];
        save(IndividualRunMatrix, 'tACS_Ind_run_Psame')
 end
tACS_all_Psame=[tACS_all_min_pars_Psame,tACS_all_min_NLL_Psame];
save('tACS_all_Psame', 'tACS_all_Psame')


%% Study tACS - Model comparison
n_model=2; 
tACS_LL_BCI_Psame=tACS_all_Psame(:,10).*-1;
tACS_LL_BCI_Sigma=tACS_all_Sigma(:,8).*-1;

NLL_allmodels=[tACS_LL_BCI_Sigma, tACS_LL_BCI_Psame];
LL_allmodels=NLL_allmodels.*-1;

% VBA analysis
[posterior,out] = VBA_groupBMC(LL_allmodels') ;
f  = out.Ef ;
EP = out.ep ;
PEP = (1-out.bor)*out.ep + out.bor/length(out.ep);

% AIC / BIC
n_comparison=1;
n_RandomDraw = 1000000;
numParam=[7, 9];
numObs  = 420; % rep x asynch x noise level
aic=NaN(tACS_n_subj, n_model); bic=NaN(tACS_n_subj, n_model);      

for subj=1:tACS_n_subj
aic(subj,:) = 2*numParam(1,:) - 2*LL_allmodels(subj,:);
bic(subj,:) = log(numObs)*numParam(1,:) - 2*LL_allmodels(subj,:);
end

% col 1: 1 vs 2 
DiffAIC=aic(:,1)-aic(:,2);   
DiffBIC=bic(:,1)-bic(:,2);      
% Raw sum
SumAICdiffs = sum(DiffAIC); SumBICdiffs = sum(DiffBIC);
% AIC
RandSumAICdiffs = NaN(n_comparison,n_RandomDraw);
aic_ci_lowerbound=NaN(n_comparison,1); aic_ci_upperbound=NaN(n_comparison,1);
for comp=1:n_comparison
for i = 1:n_RandomDraw

    RandAICdiffs = randsample(DiffAIC(:,comp), tACS_n_subj, 1);
    RandSumAICdiffs(comp,i) = sum(RandAICdiffs);

end
aic_ci_lowerbound(comp,1) = quantile(RandSumAICdiffs(comp,:), 0.025);
aic_ci_upperbound(comp,1) = quantile(RandSumAICdiffs(comp,:), 0.975);

end

% BIC
RandSumBICdiffs = NaN(n_comparison,n_RandomDraw);
BIC_ci_lowerbound=NaN(n_comparison,1); BIC_ci_upperbound=NaN(n_comparison,1);
for comp=1:n_comparison
for i = 1:n_RandomDraw

    RandBICdiffs = randsample(DiffBIC(:,comp), tACS_n_subj, 1);
    RandSumBICdiffs(comp,i) = sum(RandBICdiffs);

end
BIC_ci_lowerbound(comp,1) = quantile(RandSumBICdiffs(comp,:), 0.025);
BIC_ci_upperbound(comp,1) = quantile(RandSumBICdiffs(comp,:), 0.975);

end

Res_tACS=[aic_ci_lowerbound, SumAICdiffs', aic_ci_upperbound, BIC_ci_lowerbound, SumBICdiffs', BIC_ci_upperbound];

