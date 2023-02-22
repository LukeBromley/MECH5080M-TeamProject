import matplotlib as mpl
import matplotlib.pyplot as plt

r1 = mpl.patches.Rectangle((0.0,0.0),2.0,3.0)
r2 = mpl.patches.Rectangle((0.0,0.0),3.0,2.0)
r3 = mpl.patches.Rectangle((10.0,10.0),2.0,3.0)

r1.set_color('r')
r2.set_color('g')
r3.set_color('b')

rs = [r1,r2,r3]

for (fi,f) in enumerate(rs):
    for (si,s) in enumerate(rs):
        pc = f.get_path().intersects_path(s.get_path())
        bbc = f.get_path().intersects_bbox(s.get_bbox())
        print (fi,si,'path intersection', pc , 'bbox intersection',bbc)

fig = plt.figure(None)
ax = fig.gca()

for p in rs:
    ax.add_patch(p)

plt.show()