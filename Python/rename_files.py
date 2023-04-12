import os

dir = "./90deg/"

f = []
for (dirpath, dirnames, filenames) in os.walk(dir):
    f.extend(filenames)
    break

header = "Coordinates.Image X [Pixel],Coordinates.Image Y [Pixel],coor.X [mm],coor.Y [mm],disp.Horizontal Displacement U [mm],disp.Vertical Displacement V [mm],strain.Strain-global frame: Exx [ ],strain.Strain-global frame: Eyy [ ],strain.Strain-global frame: Exy [ ]"

for file_name in filenames:
    os.rename(dir+file_name, dir+file_name.replace("_0", ""))
    with open(dir+file_name, "r") as f:
        f.readline()
        filecontents = f.read()

    new = filecontents.replace(" ", ",")

    with open(dir+file_name, 'w') as f:
        f.write(header+"\n")
        f.write(new)