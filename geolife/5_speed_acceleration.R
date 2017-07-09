library(geosphere)
library(ggplot2)

# Distance using Haversine function
distance <- function(latitude1, longitude1, latitude2, longitude2) {
  earthRadius <- 6371000
  d <- distHaversine(c(longitude2, latitude2), c(longitude1, latitude1), earthRadius)
  return(d)
}


file_dir <- 'output'
filename <- 'tmp_final.csv'
options(digits = 14)
traces <- read.csv(paste0(file_dir, '/', filename),
                   colClasses = c("numeric",
                                  "numeric",
                                  "numeric",
                                  "numeric",
                                  "numeric",
                                  "numeric",
                                  "numeric",
                                  "numeric",
                                  "numeric",
                                  "character"
                   ),
                   numeral=c("no.loss")
)

traces <- traces[order(traces$userid, traces$timestamp),]
users <- levels(as.factor(traces$userid))
# 1. Calculate Delta Timestamps
traces$delta_timestamp <- 0
for (user in users) {
  traces_per_group <- traces[(traces$userid == user), ]
  timestamps <- traces_per_group$timestamp
  first_timestamp <- timestamps[1]
  timestamps_displaced <- head(timestamps, -1)
  timestamps_displaced <- c(first_timestamp, timestamps_displaced)
  traces[(traces$userid == user), c("delta_timestamp")] <- timestamps - timestamps_displaced
}
# [Zheng]
# 2. Divide the trajectory into different trips > 20 min
traces$trip <- 1
trip_n <- 1
trip_number <- function(t) {
  if(t > 20*60) {
    trip_n <<- trip_n + 1
  }
  return(trip_n)
}
for (user in users) {
  trip_n <- trip_n + 1
  deltas <- traces[traces$userid == user, c("delta_timestamp")]
  tr <- mapply(trip_number, deltas)
  traces[traces$userid == user, c("trip")] <- tr
}
# 3. Calculate the distances to the previous point using heversine distance
traces$distance <- 0
for (user in users) {
  latitude2 <- traces[traces$userid == user, c("latitude")]
  longitude2 <- traces[traces$userid == user, c("longitude")]
  latitude1 <- head(latitude2, -1)
  latitude1 <- c(latitude2[1], latitude1)
  longitude1 <- head(longitude2, -1)
  longitude1 <- c(longitude2[1], longitude1)
  d <- mapply(distance, latitude1, longitude1, latitude2, longitude2)
  traces[traces$userid == user, c('distance')] <- d
}
# 4. Calculate Speed
calculate_speed <- function(d, t) {
  sp <- 0
  eps_t <- 0.000001
  if(t > eps_t) {
    sp <- (d/t)
  }
  return(sp)
}
traces$speed <- 0
s <- mapply(calculate_speed, traces$distance, traces$delta_timestamp)
traces$speed <- s
# 5. Calculate Acceleration
calculate_acc <- function(sp, t) {
  acc <- 0
  eps_t <- 0.000001
  if(t > eps_t) {
    acc <- (sp/t)
  }
  return(acc)
}
traces$acceleration <- 0
acc <- mapply(calculate_acc, traces$speed, traces$delta_timestamp)
traces$acceleration <- acc
# DONT DO THIS [Zheng] <- IT DIDNT WORK
# N <- Not defined
# W <- Walk Point
# NW <- Non Walk Point
sp_th <- 2.78 #[Schuessler]
a_th <- 0.1   #[Schuessler]
traces$type1 <- "NW"
w <- (traces$speed < sp_th) & (traces$acceleration < a_th)
traces[w, "type1"] <- "W"
# This limits dont work

# 6. Isolate the first points in a trip
traces$first <- FALSE
trips <- traces$trip
trips_displaced <- head(trips, -1)
trips_displaced <- c(-1, trips_displaced)
traces$first <- (trips - trips_displaced) != 0

# Some boxplot graphs
traces_no_first <- traces[!traces$first, ]
gbox <- ggplot(data = traces_no_first, aes(x = label, y = speed))
gbox <- gbox + geom_boxplot(outlier.colour="red", outlier.shape=8,
                            outlier.size=4)

gbox <- ggplot(data = traces_no_first, aes(x = label, y = acceleration))
gbox <- gbox + geom_boxplot(outlier.colour="red", outlier.shape=8,
                            outlier.size=4)

# 7. Mark the beginning of a label
traces$first_label <- FALSE
labels <- traces$label
labels_displaced <- head(labels, -1) 
labels_displaced <- c("none", labels_displaced)
traces$first_label <- labels != labels_displaced
# 8. Generate the number of the segment inside each trip
traces$segment <- 1
segment_n <- 1
segment_number <- function(t, tt) {
  # If it is the first labeled point or if it is the first in the trip
  # Increment the segment count
  if(t | tt) {
    segment_n <<- segment_n + 1
  }
  return(segment_n)
}
segments <- mapply(segment_number, traces$first_label, traces$first)
traces$segment <- segments
# 9. Generate the first in a segment
traces$first_segment <- FALSE
segments <- traces$segment
segments_displaced <- head(segments, -1) 
segments_displaced <- c("none", segments_displaced)
traces$first_segment <- segments != segments_displaced

# What is the mínimum number of captures per segment?
seg_agg <- aggregate(trace_id~segment, traces, FUN=length)
s <- cbind(seg_agg)
mean(s$trace_id)
min(s$trace_id)
sd(s$trace_id)

# 10. Write to a file
filename <- "final_dataset.csv"
write.csv(traces, paste0(file_dir, '/', filename), row.names = FALSE)