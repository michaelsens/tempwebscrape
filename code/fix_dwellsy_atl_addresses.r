

library(leaflet)
library(sf)
library(tidyverse)


# load relevant data
atl_boundaries <- tigris::places(state='GA') %>% filter(NAME == 'Atlanta')
all_listings <- read_csv('../data/atlanta_all_listings_2021.csv') 
atl_listings <- all_listings %>% filter(address_city == 'Atlanta')

# create map for visual check
leaflet() %>%
    addProviderTiles(providers$CartoDB.Positron) %>%
    addPolygons(data = atl_boundaries, 
                color = 'black', 
                weight = 1, 
                fillOpacity = 0.1, 
                fillColor = 'grey') %>%
    addCircles(data = atl_listings, 
               lng = ~longitude, 
               lat = ~latitude,
               popup = ~building_name)


# identify observations that fall within Atlanta proper
all_listings <- st_as_sf(all_listings, coords = c("longitude", "latitude"), crs = st_crs(atl_boundaries))

within <- lengths(st_intersects(all_listings, atl_boundaries$geometry[1])) > 0
all_listings$within_atlanta <- ifelse(within, 1, 0)

write.csv(all_listings, '../output/atlanta_listings_within_checked.csv', row.names = FALSE)
