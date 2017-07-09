file_dir <- 'output'
filename <- 'dataset.csv'
output_filename <- 'dataset_50.csv'

# Dataset file is:
# id
# userid
# latitude
# longitude
# altitude
# timestamp

options(digits = 13)
geo_data <- read.csv(paste0(file_dir, '/', filename),
                 colClasses = c("numeric",
                                "numeric",
                                "numeric",
                                "numeric",
                                "numeric",
                                "numeric"
                 ),
                 numeral=c("no.loss")
)

sampled_data = data.frame(
  id = numeric(),
  userid = numeric(),
  latitude = numeric(),
  longitude = numeric(),
  altitude = numeric(),
  timestamp = numeric()
)
geo_data <- geo_data[order(geo_data$userid, geo_data$timestamp), ]
users <- levels(as.factor(geo_data$userid))
for (user in users){
  print(user)
  user_data <- geo_data[geo_data$userid == user, ]
  select <- nrow(user_data) * 0.5
  sampled_data <- rbind(sampled_data, head(user_data, select)[,c('id','userid','latitude', 'longitude', 'altitude', 'timestamp')])
}

# Write sampled data to a file:
write.csv(sampled_data, file=paste0(file_dir, '/', output_filename), row.names = FALSE)