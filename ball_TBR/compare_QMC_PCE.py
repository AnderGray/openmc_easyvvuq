from openmc_UQ_PCE import results as results_PCE
from openmc_UQ_QMC import results as results_QMC
import matplotlib.pyplot as plt
import numpy as np

samps = results_QMC.samples

mean = results_PCE.describe("TBR", "mean")
var = results_PCE.describe("TBR", "var")

dist = results_PCE.get_distribution(qoi = 'TBR')

samps_sort = np.sort(np.array(samps['TBR']).squeeze())
iis = np.linspace(0,1,samps_sort.size)

xs = np.linspace(mean - 3 *np.sqrt(var), mean + 3 *np.sqrt(var), 150)

plt.plot(xs, dist.cdf(xs), label = "PCE")
plt.step(samps_sort, iis, label = "QMC")

plt.title(f"PCE - QMC comparison")
plt.xlabel("TBR")
plt.ylabel("cdf")
plt.legend()
plt.savefig("PCE_QMC_compare.png")
plt.show()


plt.plot(xs, dist.pdf(xs))
plt.hist(samps['TBR'], 50, density=True)
plt.title(f"PCE - QMC comparison")
plt.xlabel("TBR")
plt.ylabel("pdf")
plt.savefig(f"PCE_QMC_compare_dens.png")
plt.show()

#results.plot_moments(qoi="TBR", ylabel="Temperature", xlabel="Time", alpha=0.2)
# results.plot_sobols_first(
#     qoi="te", xlabel="Time",
#     filename=os.path.join(campaign_work_dir, 'Te.png')
# )