package com.travelassistant.flight.specification;

import com.travelassistant.flight.dto.FlightSearchCriteria;
import com.travelassistant.flight.entity.Flight;
import jakarta.persistence.criteria.CriteriaBuilder;
import jakarta.persistence.criteria.CriteriaQuery;
import jakarta.persistence.criteria.Predicate;
import jakarta.persistence.criteria.Root;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.util.StringUtils;

import java.util.ArrayList;
import java.util.List;

public class FlightSpecificationBuilder {

    public static Specification<Flight> build(FlightSearchCriteria criteria) {
        return (Root<Flight> root, CriteriaQuery<?> query, CriteriaBuilder cb) -> {
            List<Predicate> predicates = new ArrayList<>();

            // 出发地 - 精确匹配
            if (StringUtils.hasText(criteria.getOrigin())) {
                predicates.add(cb.equal(root.get("origin"), criteria.getOrigin()));
            }

            // 目的地 - 精确匹配
            if (StringUtils.hasText(criteria.getDestination())) {
                predicates.add(cb.equal(root.get("destination"), criteria.getDestination()));
            }

            // 航班号 - 模糊匹配
            if (StringUtils.hasText(criteria.getFlightNo())) {
                predicates.add(cb.like(root.get("flightNo"), "%" + criteria.getFlightNo() + "%"));
            }

            // 航空公司 - 精确匹配
            if (StringUtils.hasText(criteria.getAirline())) {
                predicates.add(cb.equal(root.get("airline"), criteria.getAirline()));
            }

            // 出发日期范围
            if (criteria.getDepartureDateStart() != null) {
                predicates.add(cb.greaterThanOrEqualTo(root.get("departureDate"), criteria.getDepartureDateStart()));
            }
            if (criteria.getDepartureDateEnd() != null) {
                predicates.add(cb.lessThanOrEqualTo(root.get("departureDate"), criteria.getDepartureDateEnd()));
            }

            // 返回日期范围
            if (criteria.getReturnDateStart() != null) {
                predicates.add(cb.greaterThanOrEqualTo(root.get("returnDate"), criteria.getReturnDateStart()));
            }
            if (criteria.getReturnDateEnd() != null) {
                predicates.add(cb.lessThanOrEqualTo(root.get("returnDate"), criteria.getReturnDateEnd()));
            }

            // 价格范围
            if (criteria.getMinPrice() != null) {
                predicates.add(cb.greaterThanOrEqualTo(root.get("price"), criteria.getMinPrice()));
            }
            if (criteria.getMaxPrice() != null) {
                predicates.add(cb.lessThanOrEqualTo(root.get("price"), criteria.getMaxPrice()));
            }

            // 时长范围
            if (criteria.getMinDuration() != null) {
                predicates.add(cb.greaterThanOrEqualTo(root.get("duration"), criteria.getMinDuration()));
            }
            if (criteria.getMaxDuration() != null) {
                predicates.add(cb.lessThanOrEqualTo(root.get("duration"), criteria.getMaxDuration()));
            }

            // 处理排序
            if (StringUtils.hasText(criteria.getSortBy())) {
                String sortBy = criteria.getSortBy();
                // 处理嵌套属性或特殊字段映射
                if ("createdAt".equals(sortBy)) {
                    sortBy = "createdAt";
                } else if ("updatedAt".equals(sortBy)) {
                    sortBy = "updatedAt";
                }

                String direction = criteria.getSortDirection() != null
                    ? criteria.getSortDirection().toLowerCase()
                    : "desc";

                if ("asc".equals(direction)) {
                    query.orderBy(cb.asc(root.get(sortBy)));
                } else {
                    query.orderBy(cb.desc(root.get(sortBy)));
                }
            }

            return cb.and(predicates.toArray(new Predicate[0]));
        };
    }
}
