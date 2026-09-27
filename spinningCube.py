import math
import sys
import time

WIDTH, HEIGHT = 80, 40
ASPECT_RATIO_CORRECTION = 2.2  

SHADE_SCALE = ".:-=+*#%@"

LIGHT_SOURCE = (1.0, -1.0, -1.0)
_light_mag = math.sqrt(sum(i**2 for i in LIGHT_SOURCE))
LIGHT_SOURCE = (LIGHT_SOURCE[0]/_light_mag, LIGHT_SOURCE[1]/_light_mag, LIGHT_SOURCE[2]/_light_mag)

FACE_NORMALS = [
    (0, 0, 1),   
    (0, 0, -1),  
    (-1, 0, 0),  
    (1, 0, 0),   
    (0, -1, 0),  
    (0, 1, 0)    
]

angle_x, angle_y, angle_z = 0, 0, 0

def rotate_point(x, y, z, ax, ay, az):
    cx, sx = math.cos(ax), math.sin(ax)
    y1, z1 = y * cx - z * sx, y * sx + z * cx
    
    cy, sy = math.cos(ay), math.sin(ay)
    x2, z2 = x * cy + z1 * sy, -x * sy + z1 * cy
    
    cz, sz = math.cos(az), math.sin(az)
    x3, y3 = x2 * cz - y1 * sz, x2 * sz + y1 * cz
    
    return x3, y3, z2

try:
    step = 0.04
    intervals = [i * step for i in range(-25, 26)]
    
    faces_data = [
        ([(x, y, 1.0) for x in intervals for y in intervals], FACE_NORMALS[0]),  # Front
        ([(x, y, -1.0) for x in intervals for y in intervals], FACE_NORMALS[1]), # Back
        ([(-1.0, y, z) for y in intervals for z in intervals], FACE_NORMALS[2]), # Left
        ([(1.0, y, z) for y in intervals for z in intervals], FACE_NORMALS[3]),  # Right
        ([(x, -1.0, z) for x in intervals for z in intervals], FACE_NORMALS[4]), # Top
        ([(x, 1.0, z) for x in intervals for z in intervals], FACE_NORMALS[5])   # Bottom
    ]

    print("\033[2J", end="")

    while True:
        frame_buffer = [[' ' for _ in range(WIDTH)] for _ in range(HEIGHT)]
        z_buffer = [[0.0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        
        for surface_points, normal in faces_data:
            nx, ny, nz = rotate_point(normal[0], normal[1], normal[2], angle_x, angle_y, angle_z)
            
            if nz + 3.5 <= 0: 
                continue
                
            dot_product = nx * LIGHT_SOURCE[0] + ny * LIGHT_SOURCE[1] + nz * LIGHT_SOURCE[2]
            
            intensity = int((dot_product + 1.0) / 2.0 * (len(SHADE_SCALE) - 1))
            intensity = max(0, min(intensity, len(SHADE_SCALE) - 1))
            shade_char = SHADE_SCALE[intensity]

            for x, y, z in surface_points:
                rx, ry, rz = rotate_point(x, y, z, angle_x, angle_y, angle_z)
                
                z_depth = rz + 3.8
                ooz = 1.0 / z_depth
                
                scale = 30
                sx = int(WIDTH / 2 + rx * scale * ASPECT_RATIO_CORRECTION * ooz)
                sy = int(HEIGHT / 2 + ry * scale * ooz)
                
                if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
                    if ooz > z_buffer[sy][sx]:
                        z_buffer[sy][sx] = ooz
                        frame_buffer[sy][sx] = shade_char

        output = "\033[H" + '\n'.join(''.join(row) for row in frame_buffer)
        sys.stdout.write(output)
        sys.stdout.flush()

        angle_x += 0.03
        angle_y += 0.04
        angle_z += 0.015
        time.sleep(0.015)

except KeyboardInterrupt:
    print("\033[2J\033[H\nEngine shut down safely.")
