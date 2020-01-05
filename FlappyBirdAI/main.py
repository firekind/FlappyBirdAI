import os
import sys
import logging
import argparse
import traceback
from datetime import datetime

from net import Solver
from net.utils import CheckpointManager

from game import Emulator

if __name__ == "__main__":
    # creating argument parsers
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="Train or test", dest="command")

    # arguments for training the network
    trainer = subparsers.add_parser("train")
    trainer.add_argument("--exp-name", default=datetime.now().strftime("%d_%m_%Y_%H_%M_%S"), help="Name of the experiment")
    trainer.add_argument("--out-dir", default="./runs/", help="The path to the folder to store the experiment results")
    trainer.add_argument("--log-freq", default=1, type=int, help="Logging frequency (to stdout, if verbose, and to log file)")
    trainer.add_argument("--summary-freq", default=1, type=int, help="Logging frequency (to graphs, etc.)")
    trainer.add_argument("--checkpoint-freq", default=100, type=int, help="Checkpoint frequency (in frames)")
    trainer.add_argument("--batch-size", default=32, type=int, help="The batch size")
    trainer.add_argument("--lr", default=1e-4, type=float, help="The learning rate")
    trainer.add_argument("--initial-epsilon", default=1, type=float, help="The initial value of epsilon")
    trainer.add_argument("--final-epsilon", default=0.1, type=float, help="The final value of epsilon")
    trainer.add_argument("--frames-per-action", default=4, type=int, help=
                         "The number of frames to be passed before an action can be performed")
    trainer.add_argument("--max-replay", default=50000, type=int, help="Maximum size of replay memory")
    trainer.add_argument("--observe-for", default=100000, type=int, help="Number of frames to observe before training")
    trainer.add_argument("--explore", default=1000000, type=int, help="Number of frames across which the epsilon should be decreased")
    trainer.add_argument("--gamma", default=0.99, type=float, help="rate of decay of past observations")
    trainer.add_argument("--verbose", action="store_true", help="Enables verbose output.")
    trainer.add_argument("--debug", action="store_true", help="Enables debug mode")
    trainer.add_argument("--cuda", action="store_true", help="Uses cuda")

    # getting arguments
    args = parser.parse_args()

    # creating checkpoint manager
    checkpoint_mgr = CheckpointManager('model', args.out_dir, args.exp_name, frequency=args.checkpoint_freq)

    # creating logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if args.debug else logging.INFO)
    # creating formatter for the logger
    formatter = logging.Formatter("[%(asctime)s %(levelname)s] %(message)s", "%d-%m-%Y %H:%M:%S")
    # creating the log file and setting format
    file_handler = logging.FileHandler(os.path.join(checkpoint_mgr.out_dir, "log"))
    file_handler.setFormatter(formatter)
    # attaching log file to logger
    logger.addHandler(file_handler)
    # printing to stdout, if verbose
    if args.verbose:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    # attaching except hook callback
    sys.excepthook = lambda tp, val, tb: logger.error(f"Unhandled Exception:\nType: {tp}\nValue: {val}\n"
                                                      f"Traceback: {''.join(traceback.format_tb(tb))}")

    logger.info("Program started.")
    logger.info("Arguments: %s", args)
    logger.info("Logging results every %d epoch(s)", args.log_freq)

    # executing
    if args.command == "train":
        Solver(args, checkpoint_mgr).train_network()
