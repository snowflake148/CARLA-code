import carla
import time

def main() :
    try:
        # connect to server
        client = carla.Client('10.10.113.135', 2000)
        client.set_timeout(10.0)
        world = client.get_world()
        blueprint_library = world.get_blueprint_library()

        # choose car from map in library
        bp = blueprint_library.find('vehicle.audi.tt')

        # find location
        spawn_point = world.get_map().get_spawn_points()[0]
        vehicle = world.spawn_actor(bp, spawn_point)
        print("Audii TT created")

        #pick spectator from worl
        spectator = world.get_spectator()
        # pick the car's location
        transform = vehicle.get_transform()
        #put the camera of the simulator at the car
        spectator.set_transform(carla.Transform(transform.location + carla.Location(z=50), carla.Rotation(pitch = -90)))
        
        # Let the car run straight 5s
        # throttle: Ga (0.0 đến 1.0), Steer: Lái (-1.0 đến 1.0)
        vehicle.apply_control(carla.VehicleControl(throttle=1.0, steer = 0.0))
        time.sleep(20)

        # auto
        #vehicle.set_autopilot(True)

    finally:
        # clean when finish
        if vehicle:
            vehicle.destroy()
        print("Clear")

if __name__ == '__main__':
    main()

