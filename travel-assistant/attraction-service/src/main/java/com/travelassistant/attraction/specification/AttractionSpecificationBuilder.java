package com.travelassistant.attraction.specification;

import com.travelassistant.attraction.dto.AttractionSearchCriteria;
import com.travelassistant.attraction.entity.Attraction;
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

public class AttractionSpecificationBuilder {

    public static Specification<Attraction> build(AttractionSearchCriteria criteria) {
        return (Root<Attraction> root, CriteriaQuery<?> query, CriteriaBuilder cb) -> {
            List<Predicate> predicates = new ArrayList<>();

            // 目的地 - 精确匹配
            if (StringUtils.hasText(criteria.getDestination())) {
                predicates.add(cb.equal(root.get("destination"), criteria.getDestination()));
            }

            // 景点名称 - 模糊匹配
            if (StringUtils.hasText(criteria.getName())) {
                predicates.add(cb.like(root.get("name"), "%" + criteria.getName() + "%"));
            }

            // 类别 - 精确匹配
            if (StringUtils.hasText(criteria.getCategory())) {
                predicates.add(cb.equal(root.get("category"), criteria.getCategory()));
            }

            // 描述 - 模糊匹配
            if (StringUtils.hasText(criteria.getDescription())) {
                predicates.add(cb.like(root.get("description"), "%" + criteria.getDescription() + "%"));
            }

            // 营业时间 - 模糊匹配
            if (StringUtils.hasText(criteria.getOpeningHours())) {
                predicates.add(cb.like(root.get("openingHours"), "%" + criteria.getOpeningHours() + "%"));
            }

            // 评分范围
            if (criteria.getMinRating() != null) {
                predicates.add(cb.greaterThanOrEqualTo(root.get("rating"), criteria.getMinRating()));
            }
            if (criteria.getMaxRating() != null) {
                predicates.add(cb.lessThanOrEqualTo(root.get("rating"), criteria.getMaxRating()));
            }

            // 标签 - 满足任一标签即可（使用 JSONB 数组 containment 查询）
            if (criteria.getTags() != null && !criteria.getTags().isEmpty()) {
//                Join<Attraction, String> tagsJoin = root.join("tags", JoinType.INNER);
//                CriteriaBuilder.In<String> inClause = cb.in(tagsJoin);
//                for (String tag : criteria.getTags()) {
//                    inClause.value(tag);
//                }
//                predicates.add(inClause);
                // 方法：tags 数组中只要包含任一传入的标签即可
                String[] tags = criteria.getTags().toArray(new String[0]);
                // 手动拼 SQL: tags && ARRAY['tag1','tag2']
                String tagArrayStr = "ARRAY[" +
                        java.util.Arrays.stream(tags)
                                .map(t -> "'" + t.replace("'", "''") + "'")
                                .collect(java.util.stream.Collectors.joining(","))
                        + "]";

                predicates.add(cb.isTrue(
                        cb.function("arrayoverlaps", Boolean.class,
                                root.get("tags"),
                                cb.literal(tagArrayStr)  // 这里其实是字符串，会再转
                        )
                ));
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
