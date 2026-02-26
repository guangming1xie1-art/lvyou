package com.travelassistant.attraction.service;

import com.travelassistant.attraction.dto.AttractionSearchCriteria;
import com.travelassistant.attraction.dto.PageResponse;
import com.travelassistant.attraction.entity.Attraction;
import com.travelassistant.attraction.repository.AttractionRepository;
import com.travelassistant.attraction.specification.AttractionSpecificationBuilder;
import jakarta.persistence.EntityNotFoundException;
import jakarta.transaction.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;

@Service
@Transactional
public class AttractionService {

    @Autowired
    private AttractionRepository attractionRepository;

    /**
     * 动态搜索景点（支持任意参数组合）
     */
    public PageResponse<Attraction> searchAttractions(AttractionSearchCriteria criteria) {
        int page = criteria.getPage() != null ? criteria.getPage() : 0;
        int size = criteria.getSize() != null ? criteria.getSize() : 10;

        // 构建排序
        Sort sort = Sort.by(Sort.Direction.fromString(
                criteria.getSortDirection() != null ? criteria.getSortDirection().toUpperCase() : "DESC"),
                criteria.getSortBy() != null ? criteria.getSortBy() : "createdAt");

        PageRequest pageRequest = PageRequest.of(page, size, sort);

        Page<Attraction> attractionPage = attractionRepository.findAll(
                AttractionSpecificationBuilder.build(criteria),
                pageRequest);

        return PageResponse.of(
                attractionPage.getContent(),
                attractionPage.getNumber(),
                attractionPage.getSize(),
                attractionPage.getTotalElements());
    }

    /**
     * 创建景点
     */
    public Attraction createAttraction(Attraction attraction) {
        return attractionRepository.save(attraction);
    }

    /**
     * 根据ID获取景点
     */
    public Attraction getAttractionById(UUID id) {
        return attractionRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Attraction not found with id: " + id));
    }

    /**
     * 获取所有景点
     */
    public List<Attraction> getAllAttractions() {
        return attractionRepository.findAll();
    }

    /**
     * 根据目的地获取景点
     */
    public List<Attraction> getAttractionsByDestination(String destination) {
        return attractionRepository.findByDestination(destination);
    }

    /**
     * 根据类别获取景点
     */
    public List<Attraction> getAttractionsByCategory(String category) {
        return attractionRepository.findByCategory(category);
    }

    /**
     * 根据评分获取景点
     */
    public List<Attraction> getAttractionsByMinRating(BigDecimal minRating) {
        return attractionRepository.findByMinRating(minRating);
    }

    /**
     * 根据标签获取景点
     */
    public List<Attraction> getAttractionsByTag(String tag) {
        return attractionRepository.findByTag(tag);
    }

    /**
     * 根据目的地和类别获取景点
     */
    public List<Attraction> getAttractionsByDestinationAndCategory(String destination, String category) {
        return attractionRepository.findByDestinationAndCategory(destination, category);
    }

    /**
     * 根据目的地和标签获取景点
     */
    public List<Attraction> getAttractionsByDestinationAndTag(String destination, String tag) {
        return attractionRepository.findByDestinationAndTag(destination, tag);
    }

    /**
     * 根据多个标签获取景点
     */
    public List<Attraction> getAttractionsByTags(List<String> tags) {
        return attractionRepository.findByTags(tags);
    }

    /**
     * 更新景点
     */
    public Attraction updateAttraction(UUID id, Attraction updatedAttraction) {
        Attraction existingAttraction = getAttractionById(id);
        // 更新字段逻辑
        return attractionRepository.save(existingAttraction);
    }

    /**
     * 删除景点
     */
    public void deleteAttraction(UUID id) {
        Attraction attraction = getAttractionById(id);
        attractionRepository.delete(attraction);
    }
}