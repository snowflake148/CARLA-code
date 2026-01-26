import glob
import os
import sys
import time
import random

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

def process_img(image):
    if not os.path.exists('_out'):
        os.makedirs('_out')
    if image.frame % 10 == 0:
        image.save_to_disk('_out/%06d.png' % image.frame)

def on_collision(event):
    print(f"\n[VA CHAM] {event.actor.type_id} va cham {event.other_actor.type_id}")

def main():
    actor_list = []
    try:
        client = carla.Client('localhost', 2000)
        client.set_timeout(20.0) # Tang timeout len 20s
        world = client.get_world()

        # --- FIX LOI THOI GIAN: Huy che do dong bo de dung thoi gian thuc ---
        settings = world.get_settings()
        if settings.synchronous_mode:
            settings.synchronous_mode = False
            world.apply_settings(settings)

        # --- CAU HINH TRAFFIC MANAGER ---
        # Traffic Manager chiu trach nhiem lai xe tu dong
        tm = client.get_trafficmanager(8000)
        tm.set_global_distance_to_leading_vehicle(2.5) # Giu khoang cach an toan
        tm.set_synchronous_mode(False)

        world.set_weather(carla.WeatherParameters.ClearNoon)
        bp_lib = world.get_blueprint_library()
        
        vehicle_bps = bp_lib.filter('vehicle.*')
        vehicle_bps = [x for x in vehicle_bps if int(x.get_attribute('number_of_wheels')) == 4]
        vehicle_bp = random.choice(vehicle_bps)
        
        # Thu spawn nhieu lan neu vi tri bi ket
        spawn_points = world.get_map().get_spawn_points()
        vehicle = None
        for _ in range(5): # Thu toi da 5 lan
            try:
                spawn_point = random.choice(spawn_points)
                vehicle = world.spawn_actor(vehicle_bp, spawn_point)
                if vehicle:
                    break
            except:
                continue
        
        if not vehicle:
            print("Khong the spawn xe (het cho trong hoac loi map).")
            return

        actor_list.append(vehicle)
        
        # --- KICH HOAT AUTOPILOT THONG QUA TRAFFIC MANAGER PORT 8000 ---
        vehicle.set_autopilot(True, 8000)
        print(f"Xe {vehicle.type_id} dang chay Autopilot...")

        # Camera
        camera_bp = bp_lib.find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', '800')
        camera_bp.set_attribute('image_size_y', '600')
        camera_bp.set_attribute('fov', '90')
        camera_transform = carla.Transform(carla.Location(x=2.0, z=2.8))
        camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)
        actor_list.append(camera)
        camera.listen(lambda data: process_img(data))

        col_bp = bp_lib.find('sensor.other.collision')
        col_sensor = world.spawn_actor(col_bp, carla.Transform(), attach_to=vehicle)
        list.append(col_sensor)
        col_sensor.listen(lambda event: on_collision(event))

        # --- LOOP 30 GIAY ---
        spectator = world.get_spectator()
        start_time = time.time()
        duration = 30 
        
        print("Bat dau dem nguoc 30s...")

        while time.time() - start_time < duration:
            # Kiem tra xem xe con ton tai khong (lo bi destroy do loi)
            if not vehicle.is_alive:
                print("Xe da bien mat!")
                break

            transform = vehicle.get_transform()
            
            # Goc nhin thu 3 tu tren cao phia sau duoi
            spectator.set_transform(carla.Transform(
                transform.location + carla.Location(z=10, x=-5), 
                carla.Rotation(pitch=-45, yaw=transform.rotation.yaw)
            ))
            
            time.sleep(0.05)
        
        print("Da chay xong 30s.")

    except Exception as e:
        import traceback
        print(f"CO LOI NGHIE TRONG: {e}")
        traceback.print_exc() # In chi tiet loi ra de debug
    finally:
        print("Dang don dep...")
        if actor_list:
            client.apply_batch([carla.command.DestroyActor(x) for x in actor_list])
        print("Xong.")

    if __name__ == '__main__':
        main()