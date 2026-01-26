import carla
import time
import pygame
import numpy as np

# Cấu hình cửa sổ hiển thị
WIDTH = 400
HEIGHT = 300

def processing_img(image, surface):
    # chuyển đổi dữ liệu thô từ Cam sang mảng Numpy (màu RGBA)
    array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
    array = np.reshape(array, (image.height, image.width,4))
    # Loại bỏ kênh Alpha (chỉ lấy RGB)
    array = array[:,",:3"]
    #chuyển đổi để pygame có thể hiểu đc (đổi trục)
    array - array[:, :, ::1]
    image_surface = pygame.surfarray.make_surface(array.swapaxes(0,1))
    #vẽ hình ảnh lên cửa sổ display
    surface.blit(image_surface,(0,0))

def main() :
    #khởi tạo pygame
    pygame.init()
    display = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("CARLA Real-time Camera")
    vehicle = None
    camera = None

    try:
        # kết nối
        client = carla.Client('10.10.113.135', 2000)
        client.set_timeout(10.0)
        world = client.get_world()
        settings = world.get_settings()
        settings.no_rendering_mode = True # Tắt vẽ đồ họa ở cửa sổ chính
        world.apply_settings(settings)
        blueprint_library = world.get_blueprint_library()

        # chọn xe
        bp = blueprint_library.find('vehicle.audi.tt')

        # tim cho trong va tha xe
        spawn_point = world.get_map().get_spawn_points()[0]
        vehicle = world.spawn_actor(bp, spawn_point)
        print("Đã tạo xe Audi TT!")

        # thêm cam vào xe
        #tạo cam
        cam_bp = world.get_blueprint_library().find('sensor.camera.rgb')
        # chỉnh độ phân giải cam khớp với pygame
        cam_bp.set_attribute('image_size_x', str(WIDTH))
        cam_bp.set_attribute('image_size_y', str(HEIGHT))

        # đặt cam ở trên nắp capo (x=1.5, z=2.4)
        cam_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        camera = world.spawn_actor(cam_bp, cam_transform, attach_to=vehicle)
        #Lắng nghe camera và truyền dữ liệu vào hàm xử lý Pygame
        camera.listen(lambda data: processing_img(data, display))
        # hàm chạy mỗi khi cam có hình mới cho dữ liệu vào ổ cứng của máy
        #camera.listen(lambda image: image.save_to_disk('out/%06d.png' % image.frame))
        
        # vòng lặp chính để giữ cửa sổ mở
        running = True
        while running:
            # Nhấn X ở cửa sổ Pygame để tắt
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # cập nhật hiển thị
            pygame.display.flip()
            time.sleep(0.01)


        #lấy đối tượng spectator từ thế giới
        spectator = world.get_spectator()
        # lấy vị trí xe vừa tạo
        transform = vehicle.get_transform()
        #đặt cam của simulator vào đúng vị trí con xe
        spectator.set_transform(carla.Transform(transform.location + carla.Location(z=50), carla.Rotation(pitch = 50)))
        
        # cho xe chay thang 5s
        # throttle: Ga (0.0 đến 1.0), Steer: Lái (-1.0 đến 1.0)
        #vehicle.apply_control(carla.VehicleControl(throttle=1.0, steer = 0.0))
        #time.sleep(5)

        # cho xe tự chạy
        vehicle.set_autopilot(True)

    finally:
        # dọn dẹp khi tắt
        if camera:
            camera.stop() # dừng nghe
            camera.destroy()
        if vehicle:
            vehicle.destroy()
        pygame.quit()
        print("Đã tắt và dọn dẹp")

if __name__ == '__main__':
    main()

