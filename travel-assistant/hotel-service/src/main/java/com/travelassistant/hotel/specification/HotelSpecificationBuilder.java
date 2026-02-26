package com.travelassistant.hotel.specification;

import com.travelassistant.hotel.dto.HotelSearchCriteria;
import com.travelassistant.hotel.entity.Hotel;
import jakarta.persistence.criteria.CriteriaBuilder;
import jakarta.persistence.criteria.CriteriaQuery;
import jakarta.persistence.criteria.Join;
import jakarta.persistence.criteria.JoinType;
import jakarta.persistence.criteria.Predicate;
import jakarta.persistence.criteria.Root;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.util.StringUtils;

import java.util.ArrayList;
import java.util.List;

public class HotelSpecificationBuilder {

    public static Specification<Hotel> build(HotelSearchCriteria criteria) {
        return (Root<Hotel> root, CriteriaQuery<?> query, CriteriaBuilder cb) -> {
            List<Predicate> predicates = new ArrayList<>();

            // 目的地 - 精确匹配
            if (StringUtils.hasText(criteria.getDestination())) {
                predicates.add(cb.equal(root.get("destination"), criteria.getDestination()));
            }

            // 酒店名称 - 模糊匹配
            if (StringUtils.hasText(criteria.getName())) {
                predicates.add(cb.like(root.get("name"), "%" + criteria.getName() + "%"));
            }

            // 描述 - 模糊匹配
            if (StringUtils.hasText(criteria.getDescription())) {
                predicates.add(cb.like(root.get("description"), "%" + criteria.getDescription() + "%"));
            }

            // 价格范围
            if (criteria.getMinPrice() != null) {
                predicates.add(cb.greaterThanOrEqualTo(root.get("price"), criteria.getMinPrice()));
            }
            if (criteria.getMaxPrice() != null) {
                predicates.add(cb.lessThanOrEqualTo(root.get("price"), criteria.getMaxPrice()));
            }

            // 评分范围
            if (criteria.getMinRating() != null) {
                predicates.add(cb.greaterThanOrEqualTo(root.get("rating"), criteria.getMinRating()));
            }
            if (criteria.getMaxRating() != null) {
                predicates.add(cb.lessThanOrEqualTo(root.get("rating"), criteria.getMaxRating()));
            }

            // 入住日期
            if (criteria.getCheckInDate() != null) {
                predicates.add(cb.equal(root.get("checkInDate"), criteria.getCheckInDate()));
            }

            // 退住日期
            if (criteria.getCheckOutDate() != null) {
                predicates.add(cb.equal(root.get("checkOutDate"), criteria.getCheckOutDate()));
            }

            // 设施 - 满足任一设施即可（使用 JSONB 数组 containment 查询）
            if (criteria.getFacilities() != null && !criteria.getFacilities().isEmpty()) {
                Join<Hotel, String> facilitiesJoin = root.join("facilities", JoinType.INNER);
                CriteriaBuilder.In<String> inClause = cb.in(facilitiesJoin);
                for (String facility : criteria.getFacilities()) {
                    inClause.value(facility);
                }
                predicates.add(inClause);
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
