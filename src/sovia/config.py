
YEAR_1 = 2023
YEAR_2 = 2024
WMS1 = f"https://geodaten.metropoleruhr.de/dop/top_{YEAR_1}?language=ger&width=$width&height=$height&bbox=$x1,$y1,$x2,$y2&crs=EPSG:25832&format=image/png&request=GetMap&service=WMS&styles=&transparent=true&version=1.3.0&layers=top_{YEAR_1}"
WMS2 = f"https://geodaten.metropoleruhr.de/dop/top_{YEAR_2}?language=ger&width=$width&height=$height&bbox=$x1,$y1,$x2,$y2&crs=EPSG:25832&format=image/png&request=GetMap&service=WMS&styles=&transparent=true&version=1.3.0&layers=top_{YEAR_2}"
KLASSIFIZIERUNGSGRENZE = 0.5