package com.travelassistant.common.converter;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.persistence.AttributeConverter;
import jakarta.persistence.Converter;

@Converter
public class JsonbConverter<T> implements AttributeConverter<T, String> {

  private static final ObjectMapper mapper = new ObjectMapper().findAndRegisterModules();

  @Override
  public String convertToDatabaseColumn(T attribute) {
    if (attribute == null) {
      return null;
    }
    try {
      return mapper.writeValueAsString(attribute);
    } catch (JsonProcessingException e) {
      throw new IllegalArgumentException("Cannot convert to JSON: " + e.getMessage(), e);
    }
  }

  @Override
  public T convertToEntityAttribute(String dbData) {
    if (dbData == null) {
      return null;
    }
    try {
      return mapper.readValue(dbData, new TypeReference<>() {});
    } catch (JsonProcessingException e) {
      throw new IllegalArgumentException("Cannot parse JSON: " + e.getMessage(), e);
    }
  }
}
