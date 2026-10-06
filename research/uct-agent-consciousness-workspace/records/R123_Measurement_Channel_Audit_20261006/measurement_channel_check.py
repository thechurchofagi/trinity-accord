#!/usr/bin/env python3
"""R123: calibration of the R122 measurement filter, not a biological experiment.
Uses the published R122 settings; independent temporally white inputs are a
measurement null, not a theory of rat neural dynamics or of experience.
"""
import hashlib, json
from pathlib import Path
import numpy as np
from scipy.signal import lfilter

def main():
    dt, sigma, lag, truncate = .05, .075, .1, 4.0
    k = int(np.ceil(truncate*sigma/dt))
    w = np.exp(-.5*(np.arange(k+1)*dt/sigma)**2); w /= w.sum()
    rho = np.array([np.dot(w[h:],w[:len(w)-h])/np.dot(w,w)
                    if h<len(w) else 0. for h in range(9)])
    # Two independent runs at the fixed measured-channel settings.
    runs = []
    for seed in (123,124):
        x = np.random.default_rng(seed).normal(size=400_000)
        y = lfilter(w,[1.],x)[100:]
        r = [float(np.corrcoef(y[h:],y[:-h])[0,1]) for h in range(1,9)]
        runs.append({'seed':seed,'n_rows':len(y),'acf_lags_1_to_8':r,
                     'raw_lag1_r':float(np.corrcoef(x[1:],x[:-1])[0,1]),
                     'lag1_linear_prediction_population_R2_estimate':r[0]**2})
        assert np.max(np.abs(np.array(r)-rho[1:])) < .012
    output = {'analysis':'R123 measurement-channel calibration',
              'source_commit':'bf55557992b84f6df4dfc6a924f291dfde7b976b',
              'source_file':'research/uct-agent-consciousness-workspace/records/R122_Biology_B1_B2_20261006/b2_decode.py',
              'source_blob_sha1':'df4c15e2ab0b184a9bea9cdf41091be3b4c3044a',
              'parameters':{'bin_s':dt,'sigma_s':sigma,'lag_s':lag,'truncate':truncate},
              'weights':w.tolist(),'tap_count':len(w),
              'relative_support_to_target_endpoint_s':[-dt+lag-k*dt,lag],
              'population_white_input_ACF_lags_0_to_8':rho.tolist(),
              'lag1_linear_prediction_population_R2':float(rho[1]**2),
              'effective_raw_bin_center_minus_target_endpoint_s':float(lag-dt/2-dt*np.dot(w,np.arange(len(w)))),
              'simulation_runs':runs,
              'limits':['Not new neural data','Does not change R122 results',
                        'Does not prove biological memory is artifactual',
                        'Lag1 null formula assumes independent equal-variance raw bins',
                        'T2 C2/C3 remain untested; E remains latent']}
    output['executed_script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    Path(__file__).with_name('measurement_channel_results.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output,indent=2))
if __name__=='__main__': main()
