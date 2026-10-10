%% Goal: calculate probability that the model observer will report "common cause" for a given stimulus s

    % K as a decision rule

function output = modelprediction_log_BCI(s, Psame, Lsigma, LsigmaS, lapse)
 
Sigma=exp(Lsigma); 
SigmaS=exp(LsigmaS);

K = 2 * (Sigma^2*(Sigma^2+SigmaS^2)/SigmaS^2) * (log(Psame/(1-Psame)) + (1/2)*log((Sigma^2+SigmaS^2)/Sigma^2));

if K<0
    pC1givens=0;
else
    pC1givens=normcdf(sqrt(K), s, Sigma)-normcdf(-sqrt(K), s, Sigma);
end


output = lapse * 0.5 + (1-lapse) * pC1givens;