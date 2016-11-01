import argparse
import pathlib

import yaml

from .world import World


def get_parser():
    parser = argparse.ArgumentParser(
        description='Gengine client')
    parser.add_argument(
        '--config', help='Configuration file. Default: %(default)s',
        type=pathlib.Path,
        default="config/client.yaml")
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    with args.config.open("r+") as f:
        config = yaml.load(f)
    print(args, config)
    # Load map
    with pathlib.Path(config['map']).open("r+") as f:
        world_map = yaml.load(f)

    world = World(world_map)
    player = world.main_actor

    try:
        # We import here, so, that pyglet does not start before we parsed
        # arguments. This is useful if we ask for command line help to not
        # load GUI window.
        import pyglet
        from client.graphics.window import GameWindow
        from client.graphics.scene import Scene
        from client.graphics.controller import InputController
        from client.graphics.camera import Camera

        camera = Camera(player)
        controller = InputController(camera, player)
        scene = Scene(world)
        GameWindow(world, scene, controller, camera)

        pyglet.app.run()
    except KeyboardInterrupt:
        print("Received SIG_INT. Quiting...")


if __name__ == "__main__":
    main()
