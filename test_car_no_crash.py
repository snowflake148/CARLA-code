import carla
import time

def main() :
    vehicle = None
    obstacle_sensor = None
    try:
        client = carla.Client('localhost',2000)
        client.set_timeout(10.0)
        world = client.get_world()
        blueprint_library = world.get_blueprint_library()


        bp = blueprint_library.find('vehicle.audi.tt')
        spawn_point = world.get_map().get_spawn_points()[0]
        vehicle = world.spawn_actor(bp, spawn_point)
        print("Car created")

        spectator = world.get_spectator()
        transform = vehicle.get_transform()
        spectator.set_transform(carla.Transform(transform.location + carla.Location(z=50), carla.Rotation(pitch = -90)))

        #tao cam bien vat can
        obs_bp = blueprint_library.find('sensor.other.obstacle')
        obs_bp.set_attribute('distance','10')
        obs_bp.set_attribute('hit_radius', '0.5')

        obs_transform = carla.Transform(carla.Location(x=1.5, z=1.0))
        obstacle_sensor = world.spawn_actor(obs_bp, obs_transform, attach_to = vehicle)
        #ham xu ly khi phat hien vat can
        def on_obstacle(event):
            if event.distance < 5:
                print(f"WARNING: Detected {event.other_actor.type_id} at {event.distance:.2f}m! EMERGENCY BRAKING!")
                vehicle.set_autopilot(False)
        obstacle_sensor.listen(lambda event: on_obstacle(event))

        #ket noi voi trafficmanager
        tm = client.get_trafficmanager(8000)
        #thiet lap an toan
        vehicle.set_autopilot(True, tm.get_port())
        tm.distance_to_leading_vehicle(vehicle, 5.0)
        tm.ignore_lights_percentage(vehicle, 0)
        #vong lap duy tri trang thai
        while True:
            world.wait_for_tick()
            v_trans = vehicle.get_transform()
            spectator.set_transform(carla.Transform(v_trans.location + carla.Location(z=40), carla.Rotation(pitch=-90)))

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        if vehicle:
            vehicle.destroy()
        if obstacle_sensor:
            obstacle_sensor.destroy()
        print("clear")
        
if __name__ == '__main__':
    main()

