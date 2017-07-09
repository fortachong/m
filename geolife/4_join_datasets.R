# Join the dataset 10%
# with the labels and the traces_labels
file_dir <- 'output'
filename <- 'dataset_50.csv'
options(digits = 14)
traces <- read.csv(paste0(file_dir, '/', filename),
                   colClasses = c("numeric",
                                  "numeric",
                                  "numeric",
                                  "numeric",
                                  "numeric",
                                  "numeric"
                   ),
                   numeral=c("no.loss")
)
colnames(traces)[1] <- "trace_id"

filename <- 'labels.csv'
labels <- read.csv(paste0(file_dir, '/', filename),
                   colClasses = c("numeric",
                                  "numeric",
                                  "numeric",
                                  "numeric",
                                  "character"
                   ),
                   numeral=c("no.loss")
)
colnames(labels)[1] <- "label_id"

filename <- 'traces_labels.csv'
traces_labels <- read.csv(paste0(file_dir, '/', filename),
                   colClasses = c("numeric",
                                  "numeric"
                   ),
                   numeral=c("no.loss")
)

join1 <- merge(traces, traces_labels, by="trace_id")
final_dataset <- merge(join1, labels, by="label_id")

# Some stats on labels distribution
label_dist <- aggregate(trace_id~label, final_dataset, FUN=length)
user_dist <- aggregate(trace_id~userid.x, final_dataset, FUN=length)

#label trace_id
#1  airplane     1465
#2      bike    87266
#3      boat       80
#4       bus   145419
#5       car    74566
#6       run     1406
#7    subway     9367
#8      taxi    47490
#9     train    61172
#10     walk   217576

# In [Zheng] there are only 4 classes:
# Car
# Bus
# Walk
# Bike

dt <- final_dataset[,c("label_id", "trace_id", "userid.x", "latitude", "longitude", "altitude", "timestamp", "start_timestamp", "stop_timestamp", "label")]
colnames(dt)[3] <- "userid"

# Write to a file
filename <- "tmp_final.csv"
write.csv(dt, paste0(file_dir, '/', filename), row.names = FALSE)
