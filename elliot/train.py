import argparse
import os
import shutil

from dataset.dataset import DataLoader
from recommender.traditional.BPRMF import BPRMF
from recommender.visual.VBPR import VBPR
from recommender.visual.DVBPR import DVBPR
from utils.read import read_config


def parse_args():
    parser = argparse.ArgumentParser(description="Run train of the Recommender Model.")
    parser.add_argument('--gpu', type=int, default=-1)
    parser.add_argument('--dataset', nargs='?', default='tradesy', help='dataset name: movielens, lastfm')
    parser.add_argument('--rec', nargs='?', default="dvbpr", help="bprmf, apr, random")
    parser.add_argument('--batch_size', type=int, default=128, help='batch_size')
    parser.add_argument('--k', type=int, default=150, help='top-k of recommendation.')
    parser.add_argument('--epochs', type=int, default=20, help='Number of epochs.')
    parser.add_argument('--verbose', type=int, default=4, help='number of epochs to store model parameters.')
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


def manage_directories(path_output_rec_result, path_output_rec_weight):
    if os.path.exists(os.path.dirname(path_output_rec_result)):
        shutil.rmtree(os.path.dirname(path_output_rec_result))
    os.makedirs(os.path.dirname(path_output_rec_result))
    if os.path.exists(os.path.dirname(path_output_rec_weight)):
        shutil.rmtree(os.path.dirname(path_output_rec_weight))
    os.makedirs(os.path.dirname(path_output_rec_weight))


def train():
    args = parse_args()
    path_train_data, path_test_data, path_feature_data, path_output_rec_result, path_output_rec_weight = read_config(
        sections_fields=[('PATHS', 'InputTrainFile'),
                         ('PATHS', 'InputTestFile'),
                         ('PATHS', 'FeatureFile'),
                         ('PATHS', 'OutputRecResult'),
                         ('PATHS', 'OutputRecWeight')])
    path_train_data, path_test_data, path_feature_data, = path_train_data.format(
        args.dataset), path_test_data.format(args.dataset), path_feature_data.format(args.dataset)

    if args.rec == 'bprmf' or args.rec == 'vbpr' or args.rec == 'dvbpr':
        path_output_rec_result = path_output_rec_result.format(args.dataset,
                                                               args.rec,
                                                               'emb' + str(args.embed_k),
                                                               'ep' + str(args.epochs),
                                                               'XX',
                                                               'XX')

        path_output_rec_weight = path_output_rec_weight.format(args.dataset,
                                                               args.rec,
                                                               'emb' + str(args.embed_k),
                                                               'ep' + str(args.epochs),
                                                               'XX',
                                                               'XX')
    elif args.rec == 'apr' or args.rec == 'amr':
        path_output_rec_result = path_output_rec_result.format(args.dataset,
                                                               args.rec,
                                                               'emb' + str(args.embed_k),
                                                               'ep' + str(args.epochs),
                                                               'eps' + str(args.adv_eps),
                                                               '' + args.adv_type)

        path_output_rec_weight = path_output_rec_weight.format(args.dataset,
                                                               args.rec,
                                                               'emb' + str(args.embed_k),
                                                               'ep' + str(args.epochs),
                                                               'eps' + str(args.adv_eps),
                                                               '' + args.adv_type)
    elif args.rec == 'random':
        path_output_rec_result = path_output_rec_result.format(args.dataset,
                                                               args.rec,
                                                               'XX',
                                                               'XX',
                                                               'XX',
                                                               'XX')

        path_output_rec_weight = path_output_rec_weight.format(args.dataset,
                                                               args.rec,
                                                               'XX',
                                                               'XX',
                                                               'XX',
                                                               'XX')

    # Create directories to Store Results and Rec Models
    manage_directories(path_output_rec_result, path_output_rec_weight)

    data = DataLoader(path_train_data=path_train_data,
                      path_test_data=path_test_data,
                      visual_features=path_feature_data,
                      model_name=args.rec,
                      dataset_name=args.dataset)

    print("RUNNING {0} Training on DATASET {1}".format(args.rec, args.dataset))
    print("- PARAMETERS:")
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
