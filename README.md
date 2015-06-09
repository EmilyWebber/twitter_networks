# twitter_networks
This repository contains the code for our final project for CS123 as part of the MS CAPP computer science sequence. 

######Complete code can be found in `main.py`. Other files were temporary code snippets in developing the final code.

## Our Goals
For this project, we wanted to answer the questions: What does the network of Twitter users tweeting with the hashtag `#BlackLivesMatter` look like? What is the density of this network (i.e. how connected is it)?

To answer these questions, we looked to accomplish the following (descriptions of each are below):
- [x] Collect Twitter data utilizing the Twitter API
- [x] Install MongoDB on an AWS instance in order to store collected Twitter data
- [x] Store data in MongoDB in a queryable way
- [x] Test graphing and [node eccentricity](http://en.wikipedia.org/wiki/Distance_%28graph_theory%29) code on a small network (users tweeting about `tsa`)
- [x] For each person tweeting about `BlackLivesMatter`, find their friends and followers
- [x] Build a graph of the `BlackLivesMatter` network
- [ ] Calculate node eccentricity of the `BlackLivesMatter` network utilizing MRJob to parallelize the calculations

## Step Descriptions
Each step outlined above required its own unique infrastructure and package dependencies:

__Initial Data Collection:__ We registered for [Twitter Application Keys](https://apps.twitter.com/) and used the public streaming API to collect roughly 55GB worth of Twitter data. This data consisted of raw tweets using our target text (`BlackLivesMatter`) as well as two other test sets using the text (`love` and `tsa` - "TSA" had been trending at the time of this project). Twitter data comes in JSON format.

__MongoDB:__ Since the Twitter API returns data in JSON format, we wanted to store it in a NoSQL database in order to avoid unneeded and time consuming data manipulation. We launched an EC2 instance with AWS pre-installed from the [AWS Marketplace](https://aws.amazon.com/marketplace/pp/B00CO7AVMY).

__Connecting Twitter to MongoDB__: We used a package called PyMongo (`pip install pymongo`) to connect our Twitter queries to MongoDB. MongoDB, a NoSQL database, allowed us to store the Twitter JSON files in their original format, bypassing the need to spend computational resources in order to create a new structure for the data.

__Collecting Network Data__: Once we collected Tweets, we then queried the Twitter REST API, looking for the friends and followers of each user who had tweeted about `BlackLivesMatter`. 

__Graph Analysis__: To analyze the resulting network from our Twitter collection, we used [SNAP](http://snap.stanford.edu/snappy/index.html), a scalable graph analysis package. Within this package, we measured the density of our network by calculating the __node eccentricity__ of every node. After testing this on the smaller `tsa` dataset (47,485 nodes and 63,437 edges), we attempted to use Elastic Map Reduce across 20 AWS instances in order to scale up our graph code to calculate node eccentricty for `BlackLivesMatter` (1,507,195 nodes and 3,285,611 edges).

### Challenges & Lessons Learned
We encountered challenges with each of the aforementioned steps:

__Initial Data Collection__: We originally wanted to run network analysis using past tweets (i.e. `BlackLivesMatter` around the time of Ferguson). However, this historical data is not available with the free API. This adjustment creates a limitation in terms of our analysis, since our data is limited to the window of time we were hitting the API. Additionally, we initially had many problems with `Broken pipe` errors (later rectified with the use of `screen`), leading to "incomplete" network development.

__MongoDB__: We initially attempted to [manually install MongoDB on AWS](https://mongodb-documentation.readthedocs.org/en/latest/ecosystem/tutorial/install-mongodb-on-amazon-ec2.html), followed by attempting to use the [AWS MongoDB template](https://aws.amazon.com/blogs/aws/mongodb-on-the-aws-cloud-new-quick-start-reference-deployment/), before coming across our final solution.

__Connecting Twitter to MongoDB__: Developing this infrastructure to ensure that Tweets were being collected and then stored correctly and then queryable took much longer than anticipated.

__Collecting Network Data__: This was a time-intensive process, as the Twitter REST API has [strict rate limits](https://dev.twitter.com/rest/public/rate-limits) on the number of requests in a given time window. At times, we implemented the function `time.sleep()` in order to wait for our rate limit to be lifted. In collecting this data, we also had to account for a number of errors (i.e. private user, deleted account, etc).

__Graph Analysis__: We initially hoped to visualize the resulting graph, but `graphviz` (the package suggested by SNAP) could not process such a large graph. Additionally, we struggled (or maybe not?) to parallelize the node eccentricity calculation across multiple instances.

----------------------------------------
JP's thoughts:
- considered EC2 cluster w/ S3 & EMR


For the writeup, please address:
- [x] Your dataset: size, description, format, etc.
- [x] Your hypotheses
- [x] The algorithms you used (i.e. the types of analysis you performed and how)
- [x] The big data approaches you adopted (multiple processes? threads? MapReduce? etc.); please describe in detail how you stored your data and parallelized your work
(To be clear what the difference is between the last two: the first is "we used k-nearest neighbors" and the second is "we implemented k-NN using MapReduce.")
- [ ] Talk about anything you may have learned from doing the project specifically, beyond material covered in the class
- [x] Discuss challenges, ones you overcame and ones that were insurmountable
- [ ] Share the results of your analyses and how they reflect on the hypotheses
- [ ]If you got new results or made progress since your presentation, please make sure it is clear what changed since the presentation; I don't want to miss the opportunity to give you credit for additional work
