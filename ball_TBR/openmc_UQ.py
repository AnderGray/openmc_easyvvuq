import os
import easyvvuq as uq
import chaospy as cp
import matplotlib.pyplot as plt

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

vary = { "Dens": cp.Normal(7.85, 0.15), "Enrich": cp.Uniform(40, 60) }

campaign.set_sampler(uq.sampling.PCESampler(vary=vary, polynomial_order=1))
campaign.execute().collate()

campaign.campaign_db.dump()
results = campaign.analyse(qoi_cols=['TBR'])

results.plot_sobols_treemap('TBR', figsize=(10, 10))
plt.axis('off')
results.sobols_first('TBR')
results.supported_stats()
results._get_sobols_first('TBR', 'Dens')
results._get_sobols_first('TBR', 'Enrich')
results.sobols_total('TBR', 'Dens')
