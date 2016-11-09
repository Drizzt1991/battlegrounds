import argparse
import pathlib
from logging.config import dictConfig

import yaml

from .net import NetThread
from .world import World


def get_parser():
    parser = argparse.ArgumentParser(
        description='Gengine client')
    parser.add_argument(
        '--config', help='Configuration file. Default: %(default)s',
        type=pathlib.Path,
        default="config/client.yaml")
    parser.add_argument(
        '--logging', help='Logging file. Default: %(default)s',
        type=pathlib.Path,
        default="config/logging.yaml")
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    with args.logging.open("r+") as f:
        log_conf = yaml.load(f)
        dictConfig(log_conf)

    with args.config.open("r+") as f:
        config = yaml.load(f)
    print(args, config)
    # Load map
    with pathlib.Path(config['map']).open("r+") as f:
        world_map = yaml.load(f)

    world = World(world_map)
    player = world.main_actor

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
    net = NetThread(world)
    net.start()
    GameWindow(world, scene, controller, camera)

    try:
        pyglet.app.run()
    except KeyboardInterrupt:
        print("Received SIG_INT. Quiting...")
    finally:
        net.stop()
        net.join()


if __name__ == "__main__":
    main()
