# Only select segments with this classes:
# fuse taxi and car:
library(ggplot2)
file_dir <- 'output'
filename <- 'segments_zheng.csv'
options(digits = 14)
segments <- read.csv(paste0(file_dir, '/', filename),
                   colClasses = c("numeric",
                                  "numeric",
                                  "numeric",
                                  "character",
                                  "numeric",
                                  "numeric",
                                  "numeric",
                                  "numeric",
                                  "numeric",
                                  "numeric",
                                  "numeric",
                                  "numeric",
                                  "numeric",
                                  "numeric",
                                  "numeric",
                                  "numeric",
                                  "numeric"
                   ),
                   numeral=c("no.loss")
)
s <- levels(as.factor(segments$label))
segments <- segments[segments$label %in% c("bike", "bus", "car", "taxi", "walk"),]
segments[segments$label == "taxi", c("label")] <- "car"
# Write data to file
filename <- "segments_zheng_filtered.csv"
write.csv(segments, paste0(file_dir, '/', filename), row.names = FALSE)