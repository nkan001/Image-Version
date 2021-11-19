from __future__ import print_function, division, absolute_import
import argparse
from pretrainedmodels_pytorch.examples.config import parser
import datetime
import os
import shutil
import time
import logging
from logging.handlers import RotatingFileHandler
import torch
import torch.nn as nn
import torch.backends.cudnn as cudnn
from torch.utils.tensorboard import SummaryWriter
# from torchsummary import summary
import pretrainedmodels
from recipedataset import RecipeDataset
import random
random.seed(42)
torch.manual_seed(42)

def generate_logger(filename, **log_params):
    level = log_params.setdefault('level', logging.INFO)
    logger = logging.getLogger()
    logger.setLevel(level=level)
    formatter = logging.Formatter('%(asctime)s %(filename)s:%(lineno)d %(levelname)s %(message)s')
    file_handler = RotatingFileHandler(filename, maxBytes=10 * 1024 * 1024, backupCount=3)
    file_handler.setFormatter(formatter)
    console = logging.StreamHandler()
    console.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console)

def main(args):
    generate_logger(f"{args.logdir}/log.txt")
    logging.info(args)
    writer = SummaryWriter(args.logdir) # torch.utils.Tensorboard

    # create model
    print("=> creating model '{}'".format(args.arch))
    if args.pretrained:
        logging.info("=> using pre-trained parameters '{}'".format(args.pretrained))
        model = pretrainedmodels.__dict__[args.arch](num_classes=args.num_classes,
                                                     pretrained=args.pretrained)
    else:
        model = pretrainedmodels.__dict__[args.arch](num_classes=args.num_classes)

    best_val_acc1 = 0
    # optionally resume from a checkpoint
    if args.resume:
        if os.path.isfile(args.resume):
            logging.info("=> loading checkpoint '{}'".format(args.resume))
            checkpoint = torch.load(args.resume)
            if args.train:
                args.start_epoch = checkpoint['epoch']
                best_val_acc1 = checkpoint['best_val_acc1']

            model_dict = model.state_dict()
            pretrained_dict = {k: v for k, v in checkpoint['state_dict'].items() if (k in model_dict and checkpoint['state_dict'][k].shape == model_dict[k].shape)}
            # overwrite entries in the existing state dict
            model_dict.update(pretrained_dict)
            model.load_state_dict(model_dict)  # does not load the last layer weights (output size is num_classes)

            logging.info("=> loaded checkpoint '{}' (epoch {})".format(args.resume, checkpoint['epoch']))
        else:
            logging.info("=> no checkpoint found at '{}'".format(args.resume))
    # for param_name, tensor in model.state_dict().items():
    #     print(param_name, tensor.size())
    # print(summary(model, (3, 224, 224)))
    logging.info("MODEL CONV0")
    logging.info(model.conv0)
    logging.info("MODEL LAST_LINEAR")
    logging.info(model.last_linear)

    # define loss function (criterion) and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), args.lr,
                                momentum=args.momentum,
                                weight_decay=args.weight_decay)

    if not torch.cuda.is_available():
        args.use_gpu = False
    if args.use_gpu:
        # model = torch.nn.DataParallel(model).cuda()
        model = model.cuda()
        cudnn.benchmark = True
        cudnn.deterministic = True
        criterion = criterion.cuda()

    if args.train:
        # Data loading code
        train_dataset = RecipeDataset(image_size=args.image_size,  data_dir = args.data, name = "train") # image_size same as model.input_size (by default, see config.py)
        train_loader = torch.utils.data.DataLoader(dataset=train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=args.num_workers, drop_last = True)  # num_workers = 0 to avoid mac bug
        val_dataset = RecipeDataset(image_size=args.image_size,  data_dir = args.data, name="val")
        val_loader = torch.utils.data.DataLoader(dataset=val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers,  drop_last = True)  # num_workers = 0 to avoid mac bug

        for epoch in range(args.start_epoch, args.epochs):
            lr = adjust_learning_rate(args, optimizer, epoch)

            # train for one epoch
            train_loss, train_acc1 = train(train_loader, model, criterion, optimizer, epoch, args)

            # evaluate on validation set
            val_loss, val_acc1, val_acc5 = validate(val_loader, model, criterion, args)

            # remember best prec@1 and save checkpoint
            is_best = val_acc1 > best_val_acc1
            best_val_acc1 = max(val_acc1, best_val_acc1)
            save_checkpoint({
                'epoch': epoch + 1,
                'arch': args.arch,
                'state_dict': model.state_dict(),
                'best_val_acc1': best_val_acc1,
            }, is_best, args)

            writer.add_scalar('learning_rate', lr, epoch)
            writer.add_scalar('Train/Loss', train_loss, epoch)
            writer.add_scalar('Train/Acc1', train_acc1, epoch)
            writer.add_scalar('Val/Loss', val_loss, epoch)
            writer.add_scalar('Val/Acc1', val_acc1, epoch)
            writer.flush()
        writer.close()
        args.train = False

    if not args.train:
        val_dataset = RecipeDataset(image_size=args.image_size,  data_dir = args.data, name="val")
        val_loader = torch.utils.data.DataLoader(dataset=val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers,  drop_last = True)  # num_workers = 0 to avoid mac bug
        logging.info("EVALUATING ON THE VALIDATION SET...")
        validate(val_loader, model, criterion, args)
        logging.info("EVALUATING ON THE TEST SET...")
        test_dataset = RecipeDataset(image_size=args.image_size, data_dir = args.data, name="test")
        test_loader = torch.utils.data.DataLoader(dataset=test_dataset, batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers,  drop_last = True)  # num_workers = 0 to avoid mac bug
        validate(test_loader, model, criterion, args)

def train(train_loader, model, criterion, optimizer, epoch, args):
    batch_time = AverageMeter()
    data_time = AverageMeter()
    losses = AverageMeter()
    top1 = AverageMeter()
    top5 = AverageMeter()

    # switch to train mode
    model.train()

    end = time.time()
    for i, (input, target, _id) in enumerate(train_loader):
        print("DEVICE", input.get_device(), target.get_device())
        print("SIZE", input.size(), target.size())
        # measure data loading time
        data_time.update(time.time() - end)
        print("TARGET", target)
        if args.use_gpu:
            target = target.cuda()
            input = input.cuda()
        # input_var = torch.autograd.Variable(input)
        # print("input", input_var.size()) # torchvision.transforms.ToTensor changes the (-1, H, W, C) PIL Image to channels first which is expected by the model
        # target_var = torch.autograd.Variable(target)

        # compute output
        output = model(input)#input_var)
        loss = criterion(output, target)#_var)
        # nn.CrossEntropy loss takes the model output of shape (batchsize, num_classes) and
        # a target vector of labels of shape (batchsize) and each label is 0 <= C <= num_classes-1

        # measure accuracy and record loss
        prec1, prec5 = accuracy(output.data, target, topk=(1, 5))
        losses.update(loss.data.item(), input.size(0))
        top1.update(prec1.item(), input.size(0))
        top5.update(prec5.item(), input.size(0))

        # compute gradient and do SGD step
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # measure elapsed time
        batch_time.update(time.time() - end)
        end = time.time()

        if i % args.print_freq == 0:
            logging.info('Epoch: [{0}][{1}/{2}]\t'
                         'Time {batch_time.val:.3f} ({batch_time.avg:.3f})\t'
                         'Data {data_time.val:.3f} ({data_time.avg:.3f})\t'
                         'Loss {loss.val:.4f} ({loss.avg:.4f})\t'
                         'Acc@1 {top1.val:.3f} ({top1.avg:.3f})\t'
                         'Acc@5 {top5.val:.3f} ({top5.avg:.3f})'.format(
                epoch, i, len(train_loader), batch_time=batch_time,
                data_time=data_time, loss=losses, top1=top1, top5=top5))

    return losses.avg, top1.avg


def validate(test_loader, model, criterion,args):
    with torch.no_grad():
        batch_time = AverageMeter()
        losses = AverageMeter()
        top1 = AverageMeter()
        top5 = AverageMeter()

        # switch to evaluate mode
        model.eval()

        end = time.time()
        for i, (input, target, _id) in enumerate(test_loader):
            if args.use_gpu:
                target = target.cuda()
                input = input.cuda()

            # compute output
            output = model(input)
            loss = criterion(output, target)

            # measure accuracy and record loss
            prec1, prec5 = accuracy(output.data, target.data, topk=(1, 5))
            losses.update(loss.data.item(), input.size(0))
            top1.update(prec1.item(), input.size(0))
            top5.update(prec5.item(), input.size(0))

            # measure elapsed time
            batch_time.update(time.time() - end)
            end = time.time()

            if i % args.print_freq == 0:
                logging.info('Test: [{0}/{1}]\t'
                             'Time {batch_time.val:.3f} ({batch_time.avg:.3f})\t'
                             'Loss {loss.val:.4f} ({loss.avg:.4f})\t'
                             'Acc@1 {top1.val:.3f} ({top1.avg:.3f})\t'
                             'Acc@5 {top5.val:.3f} ({top5.avg:.3f})'.format(
                    i, len(test_loader), batch_time=batch_time, loss=losses,
                    top1=top1, top5=top5))

        logging.info(' * Acc@1 {top1.avg:.3f} Acc@5 {top5.avg:.3f}'.format(top1=top1, top5=top5)) # over all batches of the validation/testing set

        return losses.avg, top1.avg, top5.avg


def save_checkpoint(state, is_best, args):
    filename = os.path.join(args.logdir, "model_last.pth")
    torch.save(state, filename)

    if is_best:
        logging.info("Saving model_best.pth...")
        bestname = os.path.join(args.logdir, "model_best.pth")
        shutil.copyfile(filename, bestname)


class AverageMeter(object):
    """Computes and stores the average and current value"""

    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count


def adjust_learning_rate(args, optimizer, epoch):
    """Sets the learning rate to the initial LR decayed by 10 every 30 epochs"""
    lr = args.lr * (0.1 ** (epoch // 30))
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr
    return lr


def accuracy(output, target, topk=(1,)):
    """Computes the precision@k for the specified values of k"""
    maxk = max(topk)
    batch_size = target.size(0)

    _, pred = output.topk(maxk, 1, True, True)
    pred = pred.t()
    # print("target shape", target.shape, "pred shape", pred.shape)
    correct = pred.eq(target.reshape(1, -1).expand_as(pred))
    # print('correct shape', correct.shape)

    res = []
    for k in topk:
        correct_k = correct[:k].reshape(-1).float().sum(0)
        res.append(correct_k.mul_(100.0 / batch_size))
    return res


if __name__ == '__main__':
    args = vars(parser.parse_args())
    args_custom = {
        "data": "dataset",
        "use_gpu": True,
        "train": False,
        "pretrained": False,
        # "epochs": 100,
        # "lr": 0.0001,
        "print_freq": 10, # batches
        "resume": "weights/model_best.pth",
        "num_classes": 6,
        "num_workers": 1,
        "batch_size": 4,
    }
    args.update(args_custom)
    args = argparse.Namespace(**args)
    if args.train:
        args.logdir = f"ImageToRecipeV2/logs/train/epochs{args.epochs}_lr{args.lr}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    else:
        args.logdir = f"ImageToRecipeV2/logs/eval/{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    os.makedirs(args.logdir, exist_ok = False)

    main(args)