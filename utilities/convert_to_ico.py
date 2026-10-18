from PIL import Image

# Ouvrir l'image et la convertir en RGBA (avec transparence)
img = Image.open("../Images/StampCatalogue.png").convert("RGBA")
datas = img.getdata()

new_data = []
for item in datas:
    # Si le pixel est presque ou totalement noir (R, G, B < 10)
    if item[0] < 10 and item[1] < 10 and item[2] < 10:
        new_data.append((0, 0, 0, 0))  # Rendre transparent
    else:
        new_data.append(item)

img.putdata(new_data)

# Enregistrer l'icône avec fond transparent
icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
img.save("StampCatalogue.ico", sizes=icon_sizes)

print("Conversion avec fond transparent terminée !")