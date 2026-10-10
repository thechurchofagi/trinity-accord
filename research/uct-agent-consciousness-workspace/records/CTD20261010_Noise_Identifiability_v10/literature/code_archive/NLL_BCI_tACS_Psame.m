function output = NLL_BCI_tACS_Psame(pars, tACS_Asynch, counts_yes, counts_no)

% Initial sets of parameters
Psame_O_Low    = pars(1);
Psame_O_Sham    = pars(2);
Psame_O_High    = pars(3);
Psame_S_Low    = pars(4);
Psame_S_Sham    = pars(5);
Psame_S_High    = pars(6);
Lsigma     = pars(7); 
LsigmaS  = pars(8); 
lapse    = pars(9); 

prediction = NaN(size(counts_yes));

for j = 1:size(counts_yes,1)        % j'th noise/orientation condition
    for i = 1:size(counts_yes, 2)   % i'th stimulus
        s_i = tACS_Asynch(i);

        % Model predictions
        switch j
            case 1
                prediction(j,i) = modelprediction_log_BCI(s_i, Psame_O_Low, Lsigma, LsigmaS, lapse);
            case 2
                prediction(j,i) = modelprediction_log_BCI(s_i, Psame_O_Sham, Lsigma, LsigmaS, lapse);
            case 3
                prediction(j,i) = modelprediction_log_BCI(s_i, Psame_O_High, Lsigma, LsigmaS, lapse);
            case 4
                prediction(j,i) = modelprediction_log_BCI(s_i, Psame_S_Low, Lsigma, LsigmaS, lapse);
            case 5
                prediction(j,i) = modelprediction_log_BCI(s_i, Psame_S_Sham, Lsigma, LsigmaS, lapse);
            case 6
                prediction(j,i) = modelprediction_log_BCI(s_i, Psame_S_High, Lsigma, LsigmaS, lapse);
                
            end
    end
end

output = - sum(sum(counts_no .* log(1-prediction))) - sum(sum(counts_yes .* log(prediction)));

