package com.travelassistant.admin.entity;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class AdminUserRoleId implements Serializable {
    private Long userId;
    private Long roleId;
}
