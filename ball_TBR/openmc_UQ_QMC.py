import os
import easyvvuq as uq
import chaospy as cp
import matplotlib.pyplot as plt
import numpy as np

import openmc
from easyvvuq.actions import CreateRunDirectory, Encode, Decode, ExecuteLocal, Actions

params = {
    "Dens": {"type": "float", "default": 7.85},
    "Enrich": {"type": "float", "default": 50}
}

encoder = uq.encoders.GenericEncoder(template_fname='openmc.template', delimiter='$', target_filename='run_model.py')

#copy_encoder_sett = uq.encoders.CopyEncoder("settings.xml", "settings.xml")
#copy_encoder_geom = uq.encoders.CopyEncoder("geometry.xml", "geometry.xml")
#copy_encoder_tallies = uq.encoders.CopyEncoder("tallies.xml", "tallies.xml")

#multi_encoder = uq.encoders.MultiEncoder(encoder, copy_encoder_sett, copy_encoder_geom, copy_encoder_tallies)

decoder = uq.decoders.JSONDecoder(target_filename='TBR.json', output_columns=['TBR'])

execute = ExecuteLocal('python3 run_model.py')

actions = Actions(CreateRunDirectory('/tmp'),
                  Encode(encoder), execute, Decode(decoder))

campaign = uq.Campaign(name='uq_openmc_', params=params, actions=actions)

vary = { "Dens": cp.Normal(7.85, 0.15), "Enrich": cp.Uniform(20, 80)}

n_samps = 2**10
#my_sampler = uq.sampling.PCESampler(vary=vary, polynomial_order=pce_order)
my_sampler = uq.sampling.qmc.QMCSampler(vary=vary, n_mc_samples = n_samps)

campaign.set_sampler(my_sampler)
campaign.draw_samples()
campaign.execute().collate()

# Post-processing analysis
my_analysis = uq.analysis.QMCAnalysis(sampler=my_sampler, qoi_cols=["TBR"])
campaign.apply_analysis(my_analysis)

# Get some descriptive statistics
results = campaign.get_last_analysis()
mean = results.describe("TBR", "mean")
var = results.describe("TBR", "var")

# Plots
samps = results.samples

plt.hist(samps['TBR'], 50)
plt.title(f"N_samples: {n_samps}")
plt.xlabel("TBR")
plt.ylabel("freq")
plt.savefig("hist_qmc.png")

samps_sort = np.sort(np.array(samps['TBR']).squeeze())
iis = np.linspace(0,1,samps_sort.size)

plt.step(samps_sort, iis)
plt.title(f"N_samples: {n_samps}")
plt.xlabel("TBR")
plt.ylabel("ecdf")
plt.savefig("ecdf_qmc.png")

#results.plot_moments(qoi="TBR", ylabel="Temperature", xlabel="Time", alpha=0.2)
# results.plot_sobols_first(
#     qoi="te", xlabel="Time",
#     filename=os.path.join(campaign_work_dir, 'Te.png')
# )