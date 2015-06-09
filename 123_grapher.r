# Most ugly, stream-of-conscious graphing code

library('ggplot2')
library('igraph')



asdf <- read.csv('~/blm_char_count.csv', header=FALSE)
qwer <- read.csv('~/love_char_count.csv', header=FALSE)


colnames(asdf) <- c("char_length", "count")
colnames(qwer) <- c("char_length", "count")

View(asdf)
View(qwer)

qplot(asdf$char_length, asdf$count, data=asdf, main='BlackLivesMatter\ntweet length distribution',
      xlab='Tweet Lengths (characters)', ylab='count')

qplot(qwer$char_length, qwer$count, data=qwer, main='love\ntweet length distribution',
      xlab='Tweet Lengths (characters)\n[some errors present]', ylab='count')


qplot(x=t.data., data=data, binwidth=1, xlab='node eccentricity', ylab='number of nodes',
      main='"tsa"\nNode Eccentricity\n(directed)')


data_u <- read.csv('/Users/jpheisel/tsa_undirected.csv', header=FALSE)
data_u <- data.frame(t(data_u))

qplot(x=t.data_u., data=data_u, binwidth=1, xlab='node eccentricity', ylab='number of nodes',
      main='"tsa"\nNode Eccentricity\n(UNdirected)')


blm <- read.graph('~/blm/xac', format='edgelist')
plot.igraph(blm, layout=layout.fruchterman.reingold, vertex.label=NA,
            edge.arrow.size=0, vertex.size=0)


blm <- read.graph('~/graphy.gv', format='edgelist')
plot.igraph(blm, layout=layout.fruchterman.reingold, vertex.label=NA,
            edge.arrow.size=0, vertex.size=0)

