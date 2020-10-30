import argparse
import os

from dataset.dataset import DataLoader
from recommender.traditional.BPRMF import BPRMF
from recommender.visual.VBPR import VBPR
from recommender.visual.DVBPR import DVBPR
from config.configs import *


def parse_args():
    parser = argparse.ArgumentParser(description="Run train of the Recommender Model.")
    parser.add_argument('--gpu', type=int, default=0)
    parser.add_argument('--dataset', nargs='?', default='tradesy', help='dataset name: movielens, lastfm')
    parser.add_argument('--rec', nargs='?', default="vbpr", help="bprmf, apr, random")
    parser.add_argument('--batch_size', type=int, default=512, help='batch_size')
    parser.add_argument('--k', type=int, default=50, help='top-k of recommendation.')
    parser.add_argument('--epochs', type=int, default=200, help='Number of epochs.')
    parser.add_argument('--verbose', type=int, default=50, help='number of epochs to store model parameters.')
    parser.add_argument('--embed_k', type=int, default=100, help='Embedding size.')
    parser.add_argument('--lr', type=float, default=1e-4, help='Learning rate.')
    parser.add_argument('--restore_epochs', type=int, default=1,
                        help='Default is 1: The restore epochs (Must be lower than the epochs)')
    parser.add_argument('--best', type=int, default=0, help='Parameter useful for attack scenario. Leave at 0 here.')

    # Parameters useful during the adv. training
    parser.add_argument('--adv_type', nargs='?', default="fgsm", help="fgsm, future work other techniques...")
    parser.add_argument('--adv_iteration', type=int, default=2, help='Iterations for BIM/PGD Adversarial Training.')
    parser.add_argument('--adv_step_size', type=int, default=4, help='Step Size for BIM/PGD ATTACK.')
    parser.add_argument('--adv_reg', type=float, default=1.0, help='Regularization for adversarial loss')
    parser.add_argument('--adv_eps', type=float, default=0.5, help='Epsilon for adversarial weights.')

    # Parameters useful during the visual recs
    parser.add_argument('--embed_d', type=int, default=20, help='size of low dimensionality')
    parser.add_argument('--lambda1', type=float, default=1.0, help='lambda1 DVBPR')
    parser.add_argument('--lambda2', type=float, default=0.001, help='lambda2 DVBPR')
    parser.add_argument('--l_w', type=float, default=1.0, help='size of low dimensionality')
    parser.add_argument('--l_b', type=float, default=1e-2, help='size of low dimensionality')
    parser.add_argument('--l_e', type=float, default=0, help='size of low dimensionality')

    return parser.parse_args()


def train():
    args = parse_args()

    if not os.path.exists(results_dir + f'/{args.dataset}'):
        os.makedirs(results_dir + f'/{args.dataset}')
    if not os.path.exists(weight_dir + f'/{args.dataset}'):
        os.makedirs(weight_dir + f'/{args.dataset}')

    data = DataLoader(params=args)

    print("TRAINING {0} ON {1}".format(args.rec, args.dataset))
    print("PARAMETERS:")
    for arg in vars(args):
        print("\t- " + str(arg) + " = " + str(getattr(args, arg)))
    print("\n")

    os.environ['CUDA_VISIBLE_DEVICES'] = str(args.gpu)

    if args.rec == 'bprmf':
        model = BPRMF(data, args)
    elif args.rec == 'vbpr':
        model = VBPR(data, args)
    elif args.rec == 'dvbpr':
        model = DVBPR(data, args)
    else:
        raise NotImplementedError('Not implemented or unknown Recommender Model.')
    model.train()


if __name__ == '__main__':
    train()
