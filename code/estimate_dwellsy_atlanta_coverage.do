
tempfile acs
	
// load and prepare 2021 5-year ACS for the Atlanta MSA
	import delimited ../output/acs_atlanta_msa_2021.csv, clear varn(1)
	g 		level = "city" if geoid == 1304000
	replace	level = "msa" if missing(level)
	collapse (sum) b*e, by(level)
	ren b25012_001e stock_total
	ren b25012_002e stock_ownerocc
	ren b25012_010e stock_rental
	save `acs'
	
	
// load Dwellsy's 2021 Atlanta listings file
	import delimited ../output/atlanta_listings_within_checked.csv, varn(1) clear bindquote(strict)
	ren geometry longitude 
	ren within_atlanta latitude
	ren v41 within_atlanta
	destring longitude, replace ignore("c(")
	destring latitude, replace ignore(")")
	destring building_number_units, replace ignore(NA)
	destring building_count_top_down, replace ignore(NA)
	replace building_number_units = building_count_top_down if missing(building_number_units)
	
	keep building_name address_city address_state building_number_units address_zip latitude longitude within_atlanta
	duplicates drop
	
	// generate unique id that accommodates properties with no addresses provided
	g lat = latitude if inlist(building_name, "Address Not Provided", "Address Not Provided Unit")
	g lon = longitude if inlist(building_name, "Address Not Provided", "Address Not Provided Unit")
	replace lat = 0 if missing(lat)
	replace lon = 0 if missing(lon)
	
	egen unique_id = group(building_name address_city address_state lat lon)
	
	// fix cases where number of units in building is incorrectly reported for only some listings
	keep unique_id building_name address_city building_number_units within_atlanta
	duplicates drop
	duplicates tag unique_id, g(foo)
	replace building_number_units = 1 if missing(building_number_units) & foo > 0
	duplicates drop
	drop foo 
	duplicates tag unique_id, g(foo)

	// fix cases where the duplicate is just an erroneous single unit count
	bys unique_id (building_number_units): ///
		replace building_number_units = building_number_units[_N] 	///
			if building_number_units[1] == 1 & building_number_units[_N] > 1 & _N == 2
	duplicates drop
	drop foo
	duplicates tag unique_id, g(foo)
	edit if foo > 0
	
	// manually remaining cases 
	replace building_number_units = 687 if unique_id == 12821
	replace building_number_units = 399 if unique_id == 12693
	replace building_number_units = 18 if unique_id == 9039
	replace building_number_units = 26 if unique_id == 5305
	replace building_number_units = 399 if unique_id == 687
	replace building_number_units = 400 if unique_id == 3106
	replace building_number_units = 1 if unique_id == 8051
	replace building_number_units = 533 if unique_id == 11144
	replace building_number_units = 393 if unique_id == 11941
	duplicates drop
	
	
	// generate city and MSA counts
	replace address_city = "Fake Atlanta" if within_atlanta == 0 & address_city == "Atlanta"
	egen city_count = sum(building_number_units), by(address_city)
	g atl_count = city_count if within_atlanta == 1
	egen unitscity = mean(atl_count)
	collapse unitscity (sum) building_number_units
	
	g market = "Atlanta"
	ren building_number_units unitsmsa
	reshape long units, i(market) j(level, str)
	
	merge 1:1 level using `acs', nogen
	g coverage = (units/stock_rental)*100
	
	