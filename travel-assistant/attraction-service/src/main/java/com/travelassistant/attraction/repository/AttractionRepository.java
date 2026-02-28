package com.travelassistant.attraction.repository;

import com.travelassistant.attraction.entity.Attraction;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.List;

@Repository
public interface AttractionRepository extends JpaRepository<Attraction, java.util.UUID>, JpaSpecificationExecutor<Attraction> {

  /**
   * 根据目的地查找景点
   */
  List<Attraction> findByDestination(String destination);

  /**
   * 根据类别查找景点
   */
  List<Attraction> findByCategory(String category);

  /**
   * 根据评分查找景点
   */
  @Query("SELECT a FROM Attraction a WHERE a.rating >= :minRating ORDER BY a.rating DESC")
  List<Attraction> findByMinRating(@Param("minRating") BigDecimal minRating);

  /**
   * 根据标签查找景点
   */
  @Query(value="SELECT a FROM Attraction a WHERE :tag = ANY(a.tags)",nativeQuery = true)
  List<Attraction> findByTag(@Param("tag") String tag);

  /**
   * 根据目的地和类别查找景点
   */
  @Query("SELECT a FROM Attraction a WHERE a.destination = :destination AND a.category = :category")
  List<Attraction> findByDestinationAndCategory(
      @Param("destination") String destination,
      @Param("category") String category);

  /**
   * 根据目的地和标签查找景点
   */
  @Query(
          value = "SELECT * FROM attractions WHERE destination = :destination AND :tag = ANY(tags)",
          nativeQuery = true
  )
  List<Attraction> findByDestinationAndTag(
          @Param("destination") String destination,
          @Param("tag") String tag);
  /**
   * 根据多个标签查找景点
   */
  @Query(
          value = "SELECT * FROM attractions WHERE tags && CAST(:tags AS text[])",
          nativeQuery = true
  )
  List<Attraction> findByTags(@Param("tags") List<String> tags);

  @Query(value = """
      SELECT * FROM attractions 
      WHERE (:destination IS NULL OR destination = :destination)
      AND (:name IS NULL OR name ILIKE '%' || :name || '%')
      AND (:category IS NULL OR category = :category)
      AND (:minRating IS NULL OR rating >= :minRating)
      AND (:maxRating IS NULL OR rating <= :maxRating)
      AND (:openingHours IS NULL OR opening_hours ILIKE '%' || :openingHours || '%')
      AND (CAST(:tags AS text[]) IS NULL OR tags && CAST(:tags AS text[]))
      ORDER BY 
          CASE WHEN :sortBy = 'rating' AND :sortDirection = 'asc' THEN rating END ASC NULLS LAST,
          CASE WHEN :sortBy = 'rating' AND :sortDirection = 'desc' THEN rating END DESC NULLS LAST,
          CASE WHEN :sortBy = 'name' AND :sortDirection = 'asc' THEN name END ASC NULLS LAST,
          CASE WHEN :sortBy = 'name' AND :sortDirection = 'desc' THEN name END DESC NULLS LAST,
          created_at DESC
      """,
          countQuery = """
      SELECT count(*) FROM attractions 
      WHERE (:destination IS NULL OR destination = :destination)
      AND (:name IS NULL OR name ILIKE '%' || :name || '%')
      AND (:category IS NULL OR category = :category)
      AND (:minRating IS NULL OR rating >= :minRating)
      AND (:maxRating IS NULL OR rating <= :maxRating)
      AND (:openingHours IS NULL OR opening_hours ILIKE '%' || :openingHours || '%')
      AND (CAST(:tags AS text[]) IS NULL OR tags && CAST(:tags AS text[]))
      """,
          nativeQuery = true)
  Page<Attraction> searchAttractions(
          @Param("destination") String destination,
          @Param("name") String name,
          @Param("category") String category,
          @Param("minRating") BigDecimal minRating,
          @Param("maxRating") BigDecimal maxRating,
          @Param("openingHours") String openingHours,
          @Param("tags") String[] tags,
          @Param("sortBy") String sortBy,
          @Param("sortDirection") String sortDirection,
          Pageable pageable
  );
}
