
rm(list = ls())

library(tidycensus)
library(tidyverse)

# set API key
readRenviron("Rsettings.mk")
census_api_key(Sys.getenv("API_KEY"))

# determine ACS variables to pull
vars <- c(
    "B25012_001E", # Total housing units
    "B25012_002E", # Total owner occupied housing units
    "B25012_010E"  # Total renter occupied housing units
)

# set MSAs to pull, with relevant state/counties
geos <- list(
    list("Atlanta", "Georgia", 
        c(
            "Fulton County", 
            "DeKalb County",
            "Gwinnett County",
            "Cobb County",
            "Clayton County",
            "Cherokee County",
            "Forsyth County",
            "Henry County",
            "Paulding County",
            "Coweta County",
            "Douglas County",
            "Fayette County",
            "Carroll County",
            "Newton County",
            "Bartow County",
            "Walton County",
            "Rockdale County",
            "Barrow County",
            "Spalding County",
            "Pickens County",
            "Haralson County",
            "Dawson County",
            "Butts County",
            "Meriwether County",
            "Morgan County",
            "Pike County",
            "Lamar County",
            "Jasper County",
            "Heard County"
        )
    )
)


# set date range for pull
dates <- c(2021)


# pull ACS data
for (y in dates) {
    for (i in 1:length(geos)) {
        c <- geos[[i]][[3]]
        p <- geos[[i]][[1]]
        s <- geos[[i]][[2]]

        dat <- get_acs("county", year = y, state = s, variables = vars, output = "wide", survey = "acs5") %>%
            filter(NAME %in% paste0(c, ", ", s))
        dat$year <- y
        dat$city <- p
        if (i == 1 & y == dates[1]) {
            out <- dat
        } else {
            out <- rbind(out, dat)
        }
    }
}

out <- rbind(
    out, 
    get_acs("place", year = 2021, state = 'GA', variables = vars, output = "wide", survey = "acs1") %>%
        filter(NAME == "Atlanta city, Georgia") %>% mutate(year = 2021, city = "Atlanta")
) 

write.csv(out, "../output/acs_atlanta_msa_2021.csv", row.names = FALSE)
