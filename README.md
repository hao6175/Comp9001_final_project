# 🌲🔥 Forest Fire Simulator

A simple forest fire simulation built with Python and Pygame.  
This project shows how a forest fire can spread and be affected by wind, rain, and humidity.

## 🧩 Features

- Trees can catch fire and burn out
- Fire spreads to nearby trees
- Wind affects the fire's direction and speed
- You can control the wind manually
- Rain slows down the fire
- Particles simulate smoke and embers

## 🎮 Controls

| Key / Mouse        | Action                      |
|--------------------|-----------------------------|
| Arrow Keys         | Change wind direction       |
| Spacebar           | Toggle rain on/off          |
| Mouse Left Click   | Start fire at clicked spot  |
| ESC or Close Window| Quit the simulation         |

## 📦 Requirements

- Python 3.x
- `pygame`
- `numpy`
- `noise` (Perlin noise)

You can install the requirements with:

```bash
pip install pygame numpy noise
```

## 🖼️ Screenshots
<img width="876" alt="截屏2025-05-20 上午1 19 41" src="https://github.com/user-attachments/assets/192ef9e6-d32b-4d8b-90a7-932ad5f30c01" />

## 🧠 How It Works
Each tree is represented by a cell in a grid.
The forest updates every frame:
Fire spreads to nearby trees based on wind and humidity.
Trees may burn out and turn to ash.
Rain reduces the chance of fire spreading.
Wind can be changed manually using arrow keys.
Smoke particles add visual realism.

##📜 License
This project is for educational and personal use.

Feel free to modify or share it — credit is appreciated!

