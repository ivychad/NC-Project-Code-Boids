from pygame import Rect, Vector2
from Constants import WIDTH, HEIGHT


class Camera:
    def __init__(self, camera_func, width, height):
        self.base_size = Vector2(width, height)
        self.camera_func = camera_func
        self.rect = Rect(0, 0, width, height)

    def _apply_vec(self, target: Vector2):
        view_range = Vector2(
            WIDTH / (self.rect.bottomright[0] - self.rect.topleft[0]),
            HEIGHT / (self.rect.bottomright[1] - self.rect.topleft[1]),
        )
        transformed_target = (
            Vector2(self.rect.topleft) + target
        ) * view_range.elementwise()
        return transformed_target

    def _apply_scalar(self, target):
        view_range = Vector2(
            WIDTH / (self.rect.bottomright[0] - self.rect.topleft[0]),
            HEIGHT / (self.rect.bottomright[1] - self.rect.topleft[1]),
        )
        return target * ((view_range.x + view_range.y) / 2)

    def apply(self, target):
        if isinstance(target, Vector2):
            return self._apply_vec(target)
        elif isinstance(target, float) or isinstance(target, int):
            return self._apply_scalar(target)

    # NOTE: Annotation `target: Boid` results in a crash (circular import)
    def update(self, target: Vector2):
        self.rect = self.camera_func(self.rect, target)

    def scale(self, scale: float):
        self.rect = Rect(self.rect.x, self.rect.y, *(self.base_size * scale))


def simple_camera(camera: Rect, target: Vector2):
    x, y = target
    _, _, w, h = camera
    return Rect(-x + w // 2, -y + h // 2, w, h)
