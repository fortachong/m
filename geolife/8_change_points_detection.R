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
# 1. In the whole file
# In [Zheng] they found that the threshold for
# walk vs non-walk in step 1 are:
# v_th = 1.8 m/s
# a_th = 0.6 m/s2
v_th = 1.8
a_th = 0.6
traces$walk <- FALSE
traces$walk <- ((traces$speed < v_th) & (traces$acceleration < a_th))

n_walk <- length(traces[traces$label == "walk", c("trace_id")])
n_non_walk <- length(traces[traces$label != "walk", c("trace_id")])
p_TP <- length(traces[(traces$label == "walk") & (traces$walk), c("trace_id")])
p_TN <- length(traces[(traces$label != "walk") & (!(traces$walk)), c("trace_id")])
p_FP <- length(traces[(traces$label != "walk") & (traces$walk), c("trace_id")])
p_FN <- length(traces[(traces$label == "walk") & (!(traces$walk)), c("trace_id")])

# 2. By trip



# Step 1: Using a loose upper bound of velocity (Vt) and 
# that of acceleration (at) to distinguish all possible 
# Walk Points from non-Walk Points.


# Step 2: If the length of a segment composed by consecutive 
# Walk Points or non-Walk Points less than a threshold, 
# merge the segment into its backward segment.

# Threshold for step 2
# 2 mts
# 2. Apply the threshold and merge segments
st_2_th <- 2
segment <- 0
segments <- c()
traces$first_walk <- FALSE
traces$last_walk <- FALSE
fw <- traces$walk
fw_1 <- fw[1]
fw_displaced <- head(fw, -1)
fw_displaced <- c(!fw_1, fw_displaced)
traces$first_walk <- fw != fw_displaced
fw_2 <- fw[length(fw)]
fw_displaced <- fw[-1]
fw_displaced <- c(fw_displaced, !fw_2)
traces$last_walk <- fw != fw_displaced
  
# Find first and last in each consecutive walk non walk
# For each user and trip

segment <- 0
traces$segment_step2 <- 0
users <- levels(as.factor(traces$userid))
for (user in users) {
  segments <- c()
  segment <- segment + 1
  tr <- traces[traces$userid == user, c("first", "walk", "distance", "first_walk", "last_walk")]
  dist <- 0
  segment_counter <- 0
  for (i in 1:nrow(tr)) {
    t <- tr[i,]
    if (t[1,4] & t[1,5]){
      dist <- 0
      # Merge with previous segment
      if (t[1,3] < st_2_th) {
        # Not sure
      }
      else {
        segment <- segment + 1
      }
      segment_counter <- 1
      segments <- c(segments, segment)
    }
    else {
      if(t[1,4]) {
        # First: Accumulate the distance
        dist <- dist + t[1,3]
        segment_counter <- 1
        segment <- segment + 1
        segments <- c(segments, segment)
      }
      else{
        if(t[1,5]) {
          if(dist + t[1,3] < st_2_th) {
            segment <- segment - 1
            segments <- c(segments, segment)
            # print(length(segments))
            # print(segment_counter)
            # print(segment)
            init <- length(segments) - segment_counter
            end <- length(segments)
            segments[init:end] <- segment
            # break
          }
          else {
            # Just add the normal segment number
            segment_counter <- segment_counter + 1
            segments <- c(segments, segment)
          }
        }
        else {
          dist <- dist + t[1,3]
          segment_counter <- segment_counter + 1
          segments <- c(segments, segment)
        }
      }
    }
  }
  traces[traces$userid == user, c("segment_step2")] <- segments
}




# segment_c <- c()
# for (i in 1:nrow(tr)) {
#   t <- tr[i,]
#   if (t[1,4] & t[1,5]){
#     dist <- 0
#     # Merge with previous segment
#     if (t[1,3] < st_2_th) {
#       # Not sure
#     }
#     else {
#       segment <- segment + 1
#     }
#     segment_counter <- 1
#     segments <- c(segments, segment)
#   }
#   else{
#     # First: Accumulate the distance
#     if(t[1,4]) {
#       dist <- dist + t[1,3]
#       segment_counter <- 1
#       segment <- segment + 1
#       segments <- c(segments, segment)
#     }
#     else {
#       # Last : Evaluate total distance
#       if(t[1,5]) {
#         if(dist + t[1,3] < st_2_th) {
#           segment <- segment - 1
#           segments <- c(segments, segment)
#           # print(length(segments))
#           # print(segment_counter)
#           # print(segment)
#           init <- length(segments) - segment_counter
#           end <- length(segments)
#           segments[init:end] <- segment
#           # break
#         }
#         else {
#           # Just add the normal segment number
#           segment_counter <- segment_counter + 1
#           segments <- c(segments, segment)
#         }
#       }
#       else {
#         dist <- dist + t[1,3]
#         segment_counter <- segment_counter + 1
#         segments <- c(segments, segment)
#       }
#     }
#   }
#   # segment_c <- c(segment_c, segment_counter)
# }
# # tr$segment_step2 <- segment_c
# tr$segment_step2 <- segments

# Step 2.5
traces$walk_step2 <- FALSE
walks_step2 <- c()
last_walk <- FALSE
walks <- tr$walk
seg <- traces$segment_step2
segment <- 0
for (i in 1:length(seg)) {
  if(seg[i] != segment) {
    last_walk <- walks[i]
    segment <- seg[i]
  }
  walks_step2 <- c(walks_step2, last_walk)
}
traces$walk_step2 <- walks_step2

# Step 3
# Step 3: If the length of a segment exceeds a certain threshold (50 mts), 
# the segment is regarded as a Certain Segment. Otherwise it is 
# deemed as an Uncertain Segment. If the number of consecutive 
# Uncertain Segment exceeds a certain threshold (3 segments), these Uncertain Segments 
# will be merged into one non-Walk Segment
step3_certain_th <- 50
traces$certain <- FALSE
traces$non_walk_step3 <- FALSE
for (user in users){
  segments_step2 <- unique(traces[traces$user == user, c("segment_step2")])
  for (segment in segments_step2) {
    dists <- traces[traces$segment_step2 == segment, c("distance")]
    if (sum(dists) > step3_certain_th) {
      traces[traces$segment_step2 == segment, c("certain")] <- TRUE
    }
  }
  cons_counter <- 0
  uncertain_segments <- c()
  possible <- c()
  for (segment in segments_step2) {
    certain <- unique(traces[traces$segment_step2 == segment, c("certain")])
    if(certain[1]){
      cons_counter <- 0
      possible <- c()
    }
    else {
      cons_counter <- cons_counter + 1
      possible <- c(possible, segment)
      if(cons_counter > 3) {
        if(length(possible) > 0){
          uncertain_segments <- c(uncertain_segments, possible)
          possible <- c()
        }
        else{
          uncertain_segments <- c(uncertain_segments, segment)
        }
      }
    }
  }
  if(length(uncertain_segments)){
    traces[traces$segment_step2 %in% uncertain_segments, c("non_walk_step3")] <- TRUE
  }
}

# segments_step2 <- levels(as.factor(tr$segment_step2))
# for (segment in segments_step2) {
#   dists <- tr[tr$segment_step2 == segment, c("distance")]
#   if (sum(dists) > step3_certain_th) {
#     tr[tr$segment_step2 == segment, c("certain")] <- TRUE
#   }
# }
# tr$non_walk_step3 <- FALSE
# cons_counter <- 0
# uncertain_segments <- c()
# possible <- c()
# for (segment in unique(tr$segment_step2)) {
#   certain <- unique(tr[tr$segment_step2 == segment, c("certain")])
#   if(certain[1]){
#     cons_counter <- 0
#     possible <- c()
#   }
#   else {
#     cons_counter <- cons_counter + 1
#     possible <- c(possible, segment)
#     if(cons_counter > 3) {
#       if(length(possible) > 0){
#         uncertain_segments <- c(uncertain_segments, possible)
#         possible <- c()
#       }
#       else{
#         uncertain_segments <- c(uncertain_segments, segment)
#       }
#     }
#   }
# }
# tr[tr$segment_step2 %in% uncertain_segments, c("non_walk_step3")] <- TRUE

# Step 4: The start point and end point of each Walk Segment are potential 
# change points, which are leveraged to partition a trip.
traces$walk_step4 <- traces$walk_step2
traces[traces$non_walk_step3, c("walk_step4")] <- FALSE


filename <- "zheng_change_points.csv"
write.csv(traces, paste0(file_dir, '/', filename), row.names = FALSE)