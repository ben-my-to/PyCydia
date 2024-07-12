# Extract initial board data
initial_board = data['game']['initialBoard']['tiles']

# Create a dictionary to store the tiles by coordinates
tiles = {}
for tile in initial_board:
    x = tile['key']['x']
    y = tile['key']['y']
    for val in tile['value']:
        z = val['key']
        value = val['value']['value']
        tiles[(x, y, z)] = value

# Function to check if a tile is playable
def is_playable(tiles, x, y, z):
    # Check if the tile is not covered by any other tile
    covered = any((x, y, z + 1) in tiles)
    
    # Check if the tile is open on the left or right
    left_open = not any((x - 1, y, z) in tiles)
    right_open = not any((x + 1, y, z) in tiles)
    
    return not covered and (left_open or right_open)

# Prepare data for plotting
x_coords = []
y_coords = []
values = []
playable = []

for (x, y, z), value in tiles.items():
    x_coords.append(x)
    y_coords.append(y)
    values.append(value)
    playable.append(is_playable(tiles, x, y, z))

# Create a 2D plot
fig, ax = plt.subplots()

# Plot each tile
for x, y, value, play in zip(x_coords, y_coords, values, playable):
    rect = patches.Rectangle((x, y), 1, 1, linewidth=1, edgecolor='black' if play else 'none', facecolor=plt.cm.viridis(value / max(values)))
    ax.add_patch(rect)

# Set plot limits and labels
ax.set_xlim(min(x_coords) - 1, max(x_coords) + 2)
ax.set_ylim(min(y_coords) - 1, max(y_coords) + 2)
ax.set_aspect('equal')
ax.set_xlabel('X Coordinate')
ax.set_ylabel('Y Coordinate')
ax.set_title('Game Board Visualization with Playable Tiles')

# Show plot
plt.show()
