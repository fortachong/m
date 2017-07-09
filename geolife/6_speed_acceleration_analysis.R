library(ggplot2)
file_dir <- 'output'
filename <- 'final_dataset.csv'
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
                                  "character",
                                  "numeric",
                                  "numeric",
                                  "numeric",
                                  "numeric",
                                  "numeric",
                                  "logical",
                                  "logical",
                                  "numeric",
                                  "logical"
                   ),
                   numeral=c("no.loss")
)

# Dont use the first points of a trip
traces_no_first <- traces[!traces$first,]

# Altitude
gbox <- ggplot(data = traces, aes(x = label, y = altitude))
gbox <- gbox + geom_boxplot(outlier.colour="red", outlier.shape=8,
                            outlier.size=4)

# Boxplots
gbox <- ggplot(data = traces_no_first, aes(x = label, y = speed))
gbox <- gbox + geom_boxplot(outlier.colour="red", outlier.shape=8,
                            outlier.size=4)

gbox <- ggplot(data = traces_no_first, aes(x = label, y = acceleration))
gbox <- gbox + geom_boxplot(outlier.colour="red", outlier.shape=8,
                            outlier.size=4)

traces_2 <- traces_no_first[traces_no_first$speed != 0 & traces_no_first$speed < 50,]
gbox <- ggplot(data = traces_2, aes(x = label, y = speed))
gbox <- gbox + geom_boxplot(outlier.colour="red", outlier.shape=8,
                            outlier.size=4)
traces_3 <- traces_2[traces_2$speed >1000,]


# Apply some limits on speed and acc to segment walk vs non-walk
traces$type1 = (traces$speed < 2.59)
# Get a terrible precision and recall

t <- traces[traces$segment %in% c(460,461,462,463),]

####################################################################################
# Analysis: Aggregates - Number of points per trip, per segment, per label
agg_trips <- aggregate(trace_id~trip, traces_no_first, FUN=length)
agg_segments <- aggregate(trace_id~segment, traces_no_first, FUN=length)
agg_labels <- aggregate(trace_id~label, traces_no_first, FUN=length)
#
# Datapoints per label
#       label trace_id
#1  airplane     1463
#2      bike    87040
#3      boat       80
#4       bus   145259
#5       car    74392
#6       run     1402
#7    subway     9335
#8      taxi    47382
#9     train    61156
#10     walk   217048

# Datapoints per segment
# Some statistics
m <- mean(agg_segments$trace_id)
s <- sd(agg_segments$trace_id)

# Scatter plot of speed and acc
gsc <- ggplot(traces_no_first, aes(x=speed, y=acceleration, color=label))
gsc <- gsc + geom_point(shape=1)

traces_less_50 <- traces_no_first[traces_no_first$speed < 50 & (traces_no_first$label %in% 
                                                                  c("bike", "bus", "car", "taxi", "subway", "train", "walk")),]
gsc <- ggplot(traces_less_50, aes(x=speed, y=acceleration, color=label))
gsc <- gsc + geom_point(shape=1)

#####################################################################################
agg_seg_number <- aggregate(distance~segment, traces_no_first, FUN=length)
agg_seg_total_distance <- aggregate(distance~segment, traces_no_first, FUN=sum)
agg_seg_total_time <- aggregate(data=traces_no_first, delta_timestamp~segment, FUN=sum)
agg_seg_mean_speed <- aggregate(speed~segment, traces_no_first, FUN=mean)
agg_seg_var_speed <- aggregate(speed~segment, traces_no_first, FUN=var)
agg_seg_mean_acceleration <- aggregate(acceleration~segment, traces_no_first, FUN=mean)

top3 <- function(x) {
  result <- c(0,0,0)
  o <- sort(x, decreasing = TRUE)
  if(!(is.na(o[1]))){
    result[1] = o[1]
  }
  if(!(is.na(o[2]))){
    result[2] = o[2]
  }
  if(!(is.na(o[3]))){
    result[3] = o[3]
  }
  return(result)
}
agg_seg_top3_speed <- aggregate(speed~segment, traces_no_first, FUN=top3)
agg_seg_top3_acceleration <- aggregate(acceleration~segment, traces_no_first, FUN=top3)

# Mergin all the segments for future 
# Select the First row in a segment
traces_no_first$first_segment <- FALSE
segments <- traces_no_first$segment
segments_displaced <- head(segments, -1)
segments_displaced <- c(-1, segments_displaced)
traces_no_first$first_segment <- (segments - segments_displaced) != 0
segments_data <- traces_no_first[traces_no_first$first_segment, c("userid", "timestamp", "label", "trip", "segment")]

# Finally merge all the aggregated data to build the dataset
m1 <- merge(segments_data, agg_seg_number, by=c("segment"))
m1 <- merge(m1, agg_seg_total_distance, by=c("segment"))
m1 <- merge(m1, agg_seg_total_time, by=c("segment"))
m1 <- merge(m1, agg_seg_mean_speed, by=c("segment"))
m1 <- merge(m1, agg_seg_var_speed, by=c("segment"))
colnames(m1)[6] <- "number_of_points"
colnames(m1)[7] <- "total_distance"
colnames(m1)[8] <- "total_time"
colnames(m1)[9] <- "mean_speed"
colnames(m1)[10] <- "var_speed"
m1 <- merge(m1, agg_seg_mean_acceleration, by=c("segment"))
colnames(m1)[11] <- "mean_acceleration"

agg_t3_1 <- cbind(agg_seg_top3_speed$speed)
colnames(agg_t3_1) <- c("speed_top_1", "speed_top_2", "speed_top_3")
agg_t3_1 <- cbind(agg_seg_top3_speed$segment, agg_t3_1)
colnames(agg_t3_1)[1] <- "segment"
agg_t3_2 <- cbind(agg_seg_top3_acceleration$acceleration)
colnames(agg_t3_2) <- c("acceleration_top_1", "acceleration_top_2", "acceleration_top_3")
agg_t3_2 <- cbind(agg_seg_top3_acceleration$segment, agg_t3_2)
colnames(agg_t3_2)[1] <- "segment"

m1 <- merge(m1, agg_t3_1, by=c("segment"))
m1 <- merge(m1, agg_t3_2, by=c("segment"))

m1[is.na(m1$var_speed), c("var_speed")] <- 0
# Write data to file
filename <- "segments_zheng.csv"
write.csv(m1, paste0(file_dir, '/', filename), row.names = FALSE)
