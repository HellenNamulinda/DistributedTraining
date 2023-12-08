# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# TODO(developer): Set your name
# Copyright © 2023 <your name>

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import bittensor as bt

from template.protocol import Train
from template.validator.reward import get_rewards
from template.utils.uids import get_random_uids
from template.utils.misc import AsyncDendritePool
import template
import asyncio


async def forward(self):
    """
    The forward function is called by the validator every time step.

    It is responsible for querying the network and scoring the responses.

    Args:
        self (:obj:`bittensor.neuron.Neuron`): The neuron object which contains all the necessary state for the validator.

    """
    miner_uids = get_random_uids(self, k=self.config.neuron.sample_size)

    datapoints_per_group = 320
    uids_per_group = 2
    numbers_of_groups = int(len(miner_uids)//uids_per_group)
    
    uid_list = [miner_uids[(i*uids_per_group):((i*uids_per_group)+uids_per_group)] if i != (numbers_of_groups-1) else miner_uids[(i*uids_per_group):] for i in range(0, numbers_of_groups)]
    # dataset_indices_list = self.dataset_common_state.get_dataset_indices(m = numbers_of_groups, n = datapoints_per_group) #TODO add repeat on blocked
    dataset_indices_list = [[1,2],[3,4],[5,6]]  

    query_tasks = []
    for index, uids in enumerate(uid_list):

        queries = []
        for uid in uids:
            #TODO get the hashes of the groups
            # Make miners return the group hashes with their losses as well.
            queries.append(
                template.protocol.Train( 
                    dataset_indices = dataset_indices_list[index],
                    run_id = self.config.neuron.run_id,
                    # initial_peers = config.initial_peers,     #TODO Add a decorator or sth for this to get the values 
                    batch_size = self.config.neuron.batch_size  #TODO let miners decide this? Based on their hardware
                )
            )

        # The dendrite client queries the network.
        query_tasks.append(
            self.dendrite_pool.async_forward(
                uids,
                queries
            )
        )
    breakpoint()
    responses = await asyncio.gather(*query_tasks)
    breakpoint()

    # Log the results for monitoring purposes.
    bt.logging.info(f"Received responses: {responses}")

    # Adjust the scores based on responses from miners.
    rewards = get_rewards(self, uids=miner_uids)

    bt.logging.info(f"Scored responses: {rewards}")
    # Update the scores based on the rewards.
    self.update_scores(rewards, miner_uids)