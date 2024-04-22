import random

import torch

from hivemind import DHT
from hivetrain.btt_connector import (
    BittensorNetwork,
    # get_validator_uids_and_addresses,
    serve_axon,
)
from hivetrain.chain_manager import LocalAddressStore
from hivetrain.config import Configurator
from hivetrain.hf_manager import LocalHFManager
from hivetrain.training_manager import MNISTTrain

from hivetrain import __spec_version__
from bittensor.btlogging import logging

import torch
import matplotlib.pyplot as plt
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Dataset, IterableDataset
from transformers import AdamW, AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset
from tqdm import tqdm

logging.info("Starting !")


def flatten_list(nested_list):
    """Flatten a nested list."""
    if nested_list and isinstance(nested_list[0], list):
        # Assumes only one level of nesting
        return [item for sublist in nested_list for item in sublist]
    return nested_list


# # set some basic configuration values
# inital_peers_request = requests.get(args.miner.bootstrapping_server)
# initial_peers = inital_peers_request.json()["initial_peers"]
# assert not (initial_peers is None)
args = Configurator.combine_configs()

BittensorNetwork.initialize(args)
my_hotkey = BittensorNetwork.wallet.hotkey.ss58_address
my_uid = BittensorNetwork.metagraph.hotkeys.index(my_hotkey)

address_store = LocalAddressStore(BittensorNetwork.subtensor, args.netuid,BittensorNetwork.wallet)
address_store.store_hf_repo(args.storage.gradient_dir)

# Parameters

batch_size = args.batch_size
epochs = 10  # Adjust epochs for MNIST training, 30_000_000_000_000_000 is unrealistic
learning_rate = 5e-5
send_interval = 60  # Every 60 seconds

# Load the MNIST dataset
transform = transforms.Compose([
    transforms.ToTensor(),  # Convert images to PyTorch tensors
    transforms.Normalize((0.5,), (0.5,))  # Normalize images
])

train_dataset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

test_dataset = datasets.MNIST(root='./data', train=False, download=True, transform=transform)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)


# Training loop
hf_manager = LocalHFManager(repo_id=args.storage.model_dir)
#def __init__(self, model_name, data_loader,gradients_dir, learning_rate=5e-5, send_interval=30):

training_loop = MNISTTrain(None, train_loader, args.storage.gradient_dir,test_loader=test_loader, send_interval=args.miner.send_interval)
#training_loop.train(epochs=1, hf_manager=hf_manager)
training_loop.save_model()
steps = [i for i in range(1000,10002,1000)]

losses = []
for step in tqdm(steps):
    losses.append(training_loop.train(epochs=30_000_000_000_000_000, hf_manager=hf_manager, n_steps = step) )



# # Assuming `steps` and `losses` are defined as you described
training_losses = [loss[0] for loss in losses]  # Extract training losses
test_losses = [loss[1] for loss in losses]      # Extract test losses
test_accuracy = [loss[2] for loss in losses]      # Extract test losses


# Plotting Training Loss over Steps
plt.figure(figsize=(10, 5))
plt.plot(steps, training_losses, label='Training Loss', color='blue')
plt.xlabel('Step')
plt.ylabel('Training Loss')
plt.title('Training Loss over Steps')
plt.legend()
plt.grid(True)
plt.savefig('training_loss.png')  # Save the plot instead of showing it
plt.close()  # Close the figure to free up memory

# Plotting Test Loss over Steps
plt.figure(figsize=(10, 5))
plt.plot(steps, test_losses, label='Test Loss', color='red')
plt.xlabel('Step')
plt.ylabel('Test Loss')
plt.title('Test Loss over Steps')
plt.legend()
plt.grid(True)
plt.savefig('test_loss.png')  # Save the plot instead of showing it
plt.close()  # Close the figure to free up memory

# Plotting Test Loss over Steps
plt.figure(figsize=(10, 5))
plt.plot(steps, test_accuracy, label='Test Accuracy', color='red')
plt.xlabel('Step')
plt.ylabel('Test Loss')
plt.title('Test Loss over Steps')
plt.legend()
plt.grid(True)
plt.savefig('test_acc.png')  # Save the plot instead of showing it
plt.close()  # Close the figure to free up memory