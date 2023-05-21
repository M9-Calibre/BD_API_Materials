import os

dir = "0deg_matchid_2d\\"

# with open(dir+"stage_metadata_unprocessed.csv", "r") as f:
#     with open(dir+"stage_metadata.csv", "w") as target:
#         for line in f:
#             content = line.split()
#             target.write(f"{content[0].replace(',','.')},{content[1].replace(',','.')},{content[3].replace(',','.')}\n")

f = []
for (dirpath, dirnames, filenames) in os.walk(dir):
    f.extend(filenames)
    break

print(f)

header = "Coordinates.Image X [Pixel],Coordinates.Image Y [Pixel],coor.X [mm],coor.Y [mm],disp.Horizontal Displacement U [mm],disp.Vertical Displacement V [mm],strain.Strain-global frame: Exx [ ],strain.Strain-global frame: Eyy [ ],strain.Strain-global frame: Exy [ ]"

for file_name in f:
    with open(dir+file_name, "r") as f:
        f.readline()
        filecontents = f.read()

    new = filecontents.replace(" ", ",")

    with open(dir+file_name, 'w') as f:
        f.write(header+"\n")
        f.write(new)
