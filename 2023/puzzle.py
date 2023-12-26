from collections import defaultdict

from PIL import Image

PUZZLE_INPUT = "puzzle2023.png"
PUZZLE_OUTPUT = "result.png"
NUMBER_OF_TILES = 675

COLOR_BACKGROUND = (30, 30, 30, 255)
COLOR_TILE_FRAME = (255, 255, 255, 255)


def is_prime(n: int) -> bool:
    """
    https://stackoverflow.com/a/15285588/483840
    """
    if n == 2 or n == 3:
        return True
    if n % 2 == 0 or n < 2:
        return False

    for i in range(3, int(n**0.5) + 1, 2):  # only odd numbers
        if n % i == 0:
            return False

    return True


def generate_output_image(grouped_tiles: dict[int, list[Image.Image]]) -> None:
    img_height = sum(height for height in grouped_tiles.keys())
    img_width = sum(tile.width for tile in next(iter(grouped_tiles.values())))
    new_img = Image.new("RGBA", (img_width, img_height))

    y = 0
    for height, tiles in grouped_tiles.items():
        x = 0
        for tile in tiles:
            new_img.paste(tile, (x, y))
            x += tile.width
        y += height

    new_img.show()
    new_img.save(PUZZLE_OUTPUT)


def group_and_sort_tiles(tiles: list[Image.Image]) -> dict[int, list[Image.Image]]:
    """
    Group rows by tile height, sort rows ascending.

    Within a row, sort columns by tile width,
    ascending if row is even, descending if row is odd.
    """
    result = defaultdict(list)
    for tile in sorted(tiles, key=lambda x: x.height):
        result[tile.height].append(tile)

    return {
        height: sorted(tile_list, key=lambda x: x.width, reverse=bool(i % 2))
        for i, (height, tile_list) in enumerate(result.items())
    }


def rotate_tiles(tiles: list[Image.Image]) -> list[Image.Image]:
    """
    Only tile width are prime, if not: rotate tile by -90deg.

    Rotate ALL tiles 180deg afterwards.
    """
    rotated_tiles = []
    for tile in tiles:
        angle = 180
        if not is_prime(tile.width):
            angle -= 90
        rotated_tile = tile.rotate(angle, expand=True)
        assert is_prime(rotated_tile.width)
        rotated_tiles.append(rotated_tile)

    return rotated_tiles


def get_tile(
    img: Image.Image, img_data, left_upper_x: int, left_upper_y: int
) -> Image.Image:
    """
    Based on the upper left corner, return the tile with the frame.
    """
    right_lower_x = left_upper_x
    while img_data[(right_lower_x, left_upper_y)] == COLOR_TILE_FRAME:
        right_lower_x += 1

    right_lower_y = left_upper_y
    while img_data[(left_upper_x, right_lower_y)] == COLOR_TILE_FRAME:
        right_lower_y += 1

    # extract image without the frame
    return img.crop(
        (left_upper_x + 1, left_upper_y + 1, right_lower_x - 1, right_lower_y - 1)
    )


if __name__ == "__main__":
    with Image.open(PUZZLE_INPUT) as img:
        img_data = img.load()

        tiles = []
        for x in range(img.width):
            for y in range(img.height):
                if (
                    img_data[(x, y)] == COLOR_TILE_FRAME
                    and img_data[(x - 1, y)] == COLOR_BACKGROUND
                    and img_data[(x - 1, y - 1)] == COLOR_BACKGROUND
                    and img_data[(x, y - 1)] == COLOR_BACKGROUND
                ):
                    tiles.append(get_tile(img, img_data, x, y))
        assert len(tiles) == NUMBER_OF_TILES

        rotated_tiles = rotate_tiles(tiles)
        grouped_tiles = group_and_sort_tiles(rotated_tiles)
        generate_output_image(grouped_tiles)
