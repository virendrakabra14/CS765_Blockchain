import matplotlib.pyplot as plt
import os
import pathlib

directory = "./outputs"
plots_dir = "./plots/"
pathlib.Path(plots_dir).mkdir(exist_ok=True)

i = 1

mean_lens = []

for dir in os.listdir(directory):
    filename = os.path.join(directory, dir, 'lengths.txt')

    with open(filename, 'r' , encoding='utf-8') as f:
        sum_len = 0
        cnt = 0
        for line in f:
            sum_len += int(line.strip())
            cnt += 1
        mean_lens.append(sum_len/cnt)

    i += 1

fig, ax = plt.subplots()

ax.scatter(list(range(1,i)), mean_lens, edgecolors='b', facecolors='none')

ax.set_xticks(list(range(i)))

ax.set_xlabel('Experiment Number')
ax.set_ylabel('Mean branch length')

ax.set_title('Mean Branch Lengths')

fig.set_size_inches(15, 8)

# plt.show()
fig.savefig(os.path.join(plots_dir, f"lengths.png"), bbox_inches="tight")
