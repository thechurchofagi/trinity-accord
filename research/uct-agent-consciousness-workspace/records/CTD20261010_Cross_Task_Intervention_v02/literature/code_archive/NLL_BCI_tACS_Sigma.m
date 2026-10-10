function output = NLL_BCI_tACS_Sigma(pars, tACS_Asynch, counts_yes, counts_no)

% Initial sets of parameters
Psame_O    = pars(1);
Psame_S    = pars(2);
LsigmaLow     = pars(3); 
LsigmaSham     = pars(4); 
LsigmaHigh     = pars(5); 
LsigmaS  = pars(6); 
lapse    = pars(7); 

prediction = NaN(size(counts_yes));

for j = 1:size(counts_yes,1)        % j'th noise/orientation condition
    for i = 1:size(counts_yes, 2)   % i'th stimulus
        s_i = tACS_Asynch(i);

        % Model predictions
        switch j
            case 1
                prediction(j,i) = modelprediction_log_BCI(s_i, Psame_O, LsigmaLow, LsigmaS, lapse);
            case 2
                prediction(j,i) = modelprediction_log_BCI(s_i, Psame_O, LsigmaSham, LsigmaS, lapse);
            case 3
                prediction(j,i) = modelprediction_log_BCI(s_i, Psame_O, LsigmaHigh, LsigmaS, lapse);
            case 4
                prediction(j,i) = modelprediction_log_BCI(s_i, Psame_S, LsigmaLow, LsigmaS, lapse);
            case 5
                prediction(j,i) = modelprediction_log_BCI(s_i, Psame_S, LsigmaSham, LsigmaS, lapse);
            case 6
                prediction(j,i) = modelprediction_log_BCI(s_i, Psame_S, LsigmaHigh, LsigmaS, lapse);
                
            end
    end
end

output = - sum(sum(counts_no .* log(1-prediction))) - sum(sum(counts_yes .* log(prediction)));

