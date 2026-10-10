function output = NLL_BCI_EEG(pars, EEG_Asynch, counts_yes, counts_no)

% Initial sets of parameters
Psame_O    = pars(1);
Psame_S    = pars(2);
Lsigma     = pars(3); 
LsigmaS  = pars(4); 
lapse    = pars(5); 

prediction = NaN(size(counts_yes));

for j = 1:size(counts_yes,1)        % j'th noise/orientation condition
    for i = 1:size(counts_yes, 2)   % i'th stimulus
        s_i = EEG_Asynch(i);

        % Model predictions
        switch j
            case 1
                prediction(j,i) = modelprediction_log_BCI(s_i, Psame_O, Lsigma, LsigmaS, lapse);
            case 2
                prediction(j,i) = modelprediction_log_BCI(s_i, Psame_S, Lsigma, LsigmaS, lapse);
            end
    end
end

output = - sum(sum(counts_no .* log(1-prediction))) - sum(sum(counts_yes .* log(prediction)));

