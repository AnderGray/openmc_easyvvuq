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

pce_order = 15
my_sampler = uq.sampling.PCESampler(vary=vary, polynomial_order=pce_order)

campaign.set_sampler(my_sampler)
campaign.draw_samples()
campaign.execute().collate()

# Post-processing analysis
my_analysis = uq.analysis.PCEAnalysis(sampler=my_sampler, qoi_cols=["TBR"])
campaign.apply_analysis(my_analysis)

# Get some descriptive statistics
results = campaign.get_last_analysis()
mean = results.describe("TBR", "mean")
var = results.describe("TBR", "var")

# Plots
xs = np.linspace(mean - 3 *np.sqrt(var), mean + 3 *np.sqrt(var), 150)

dist = results.get_distribution(qoi = 'TBR')

plt.plot(xs, dist.cdf(xs))
plt.title(f"pce order: {pce_order}")
plt.xlabel("TBR")
plt.ylabel("cdf")
plt.savefig("PCE_cdf_order_{pce_order}.png")

plt.plot(xs, dist.pdf(xs))
plt.title(f"pce order: {pce_order}")
plt.xlabel("TBR")
plt.ylabel("pdf")
plt.savefig(f"PCE_pdf_order_{pce_order}.png")

#results.plot_moments(qoi="TBR", ylabel="Temperature", xlabel="Time", alpha=0.2)
# results.plot_sobols_first(
#     qoi="te", xlabel="Time",
#     filename=os.path.join(campaign_work_dir, 'Te.png')
# )